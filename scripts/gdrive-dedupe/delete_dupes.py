#!/usr/bin/env python3
"""Trash Google Drive files listed in a JSON manifest.

Usage:
    # Dry run (default) — prints what would be trashed, makes no changes:
    python delete_dupes.py duplicates.json

    # Actually move files to Drive Trash (reversible for ~30 days):
    python delete_dupes.py duplicates.json --commit

    # Permanently delete instead of trashing (irreversible):
    python delete_dupes.py duplicates.json --commit --permanent

Auth:
    Set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON, OR run
    `gcloud auth application-default login` and grant Drive scope, OR drop a
    `credentials.json` OAuth client file next to this script and the first run
    will open a browser to authorize (token cached as `token.json`).

Manifest format (duplicates.json):
    {
      "items": [
        {"id": "<fileId>", "name": "<for log only>", "reason": "<why delete>"},
        ...
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive"]
HERE = Path(__file__).resolve().parent


def build_service():
    from googleapiclient.discovery import build

    creds = None
    sa_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if sa_path:
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(
            sa_path, scopes=SCOPES
        )
    else:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        token_path = HERE / "token.json"
        client_path = HERE / "credentials.json"
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not client_path.exists():
                    sys.exit(
                        f"No credentials. Place OAuth client JSON at {client_path} "
                        "or set GOOGLE_APPLICATION_CREDENTIALS to a service account."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(client_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            token_path.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def trash_file(service, file_id: str, permanent: bool) -> None:
    if permanent:
        service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
    else:
        service.files().update(
            fileId=file_id,
            body={"trashed": True},
            supportsAllDrives=True,
        ).execute()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("manifest", help="Path to duplicates.json")
    p.add_argument("--commit", action="store_true", help="Actually delete (default: dry run)")
    p.add_argument("--permanent", action="store_true", help="Skip trash, delete permanently")
    p.add_argument("--limit", type=int, default=0, help="Only process first N items")
    args = p.parse_args()

    data = json.loads(Path(args.manifest).read_text())
    items = data["items"]
    if args.limit:
        items = items[: args.limit]

    mode = (
        "PERMANENTLY DELETE" if args.permanent else "TRASH"
    ) if args.commit else "DRY-RUN (no changes)"
    print(f"Mode: {mode}  |  Items: {len(items)}")

    if not args.commit:
        for it in items:
            print(f"  would {('delete' if args.permanent else 'trash')}: {it['id']}  {it.get('name','')}  — {it.get('reason','')}")
        print(f"\nRun again with --commit to actually do it.")
        return 0

    service = build_service()
    ok = 0
    failed: list[tuple[str, str]] = []
    for i, it in enumerate(items, 1):
        fid = it["id"]
        label = it.get("name", "")
        try:
            trash_file(service, fid, args.permanent)
            ok += 1
            print(f"[{i}/{len(items)}] {'deleted' if args.permanent else 'trashed'}: {fid}  {label}")
        except Exception as e:
            failed.append((fid, str(e)))
            print(f"[{i}/{len(items)}] FAILED: {fid}  {label}  — {e}", file=sys.stderr)
        time.sleep(0.05)

    print(f"\nDone. ok={ok}  failed={len(failed)}")
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
