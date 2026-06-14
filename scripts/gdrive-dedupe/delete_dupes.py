#!/usr/bin/env python3
"""Trash Google Drive files listed in a JSON manifest, OR sweep all 4-byte
stub files in a given folder.

Usage:
    # Manifest mode (default). Dry run shows what would be trashed:
    python delete_dupes.py duplicates.json
    python delete_dupes.py duplicates.json --commit                # actually trash
    python delete_dupes.py duplicates.json --commit --permanent    # hard delete

    # Sweep mode — trash every 4-byte file in the given Drive folder.
    # Catches sync stubs not enumerated in the manifest:
    python delete_dupes.py --sweep-stubs 1l9JjEXwpkzSl3SXLW1lFsViMaq9CnDMJ
    python delete_dupes.py --sweep-stubs <folderId> --commit

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


def sweep_stub_folder(service, folder_id: str) -> list[dict]:
    """Return every 4-byte file directly under folder_id."""
    out: list[dict] = []
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, size, mimeType)",
            pageSize=1000,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        for f in resp.get("files", []):
            if f.get("size") == "4":
                out.append({"id": f["id"], "name": f.get("name", ""),
                            "reason": f"4-byte stub in folder {folder_id}"})
        page_token = resp.get("nextPageToken")
        if not page_token:
            return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("manifest", nargs="?", help="Path to duplicates.json (omit with --sweep-stubs)")
    p.add_argument("--commit", action="store_true", help="Actually delete (default: dry run)")
    p.add_argument("--permanent", action="store_true", help="Skip trash, delete permanently")
    p.add_argument("--limit", type=int, default=0, help="Only process first N items")
    p.add_argument("--sweep-stubs", metavar="FOLDER_ID",
                   help="Sweep mode: trash every 4-byte file in this Drive folder")
    args = p.parse_args()

    if args.sweep_stubs:
        service = build_service()
        items = sweep_stub_folder(service, args.sweep_stubs)
        print(f"Found {len(items)} 4-byte stub files in folder {args.sweep_stubs}")
    else:
        if not args.manifest:
            p.error("Provide a manifest path, or use --sweep-stubs FOLDER_ID")
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

    service = locals().get("service") or build_service()
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
