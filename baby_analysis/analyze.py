"""
Critical analysis of newborn tracking data (feeds / diapers / sleep / baths).
Produces summary stats (printed) and a multi-panel visualization dashboard.
"""
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from datetime import timedelta

plt.rcParams.update({
    "figure.dpi": 130,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

CSV = "/home/user/claude-code/baby_analysis/data.csv"
df = pd.read_csv(CSV)

# ---- parse ----
df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
df["End"]   = pd.to_datetime(df["End"], errors="coerce")

def dur_to_min(x):
    if pd.isna(x) or not isinstance(x, str) or ":" not in x:
        return np.nan
    try:
        h, m = x.split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return np.nan

df["dur_min"] = df["Duration"].apply(dur_to_min)
df["date"] = df["Start"].dt.date
df["hour"] = df["Start"].dt.hour

feeds   = df[df["Type"] == "Feed"].copy()
diapers = df[df["Type"] == "Diaper"].copy()
sleeps  = df[df["Type"] == "Sleep"].copy()
baths   = df[df["Type"] == "Bath"].copy()

# A feed with a real duration (breast session); bottle feeds have no duration
feed_sessions = feeds[feeds["dur_min"].notna()].copy()

# Birth date (config). Set to None to fall back to "study day" labelling.
BIRTH_DATE = pd.Timestamp("2026-06-05")  # DOB == first log day; tracked from birth
HAS_DOB = BIRTH_DATE is not None

span_start = df["Start"].min()
span_end   = df["Start"].max()
n_days = (span_end.normalize() - span_start.normalize()).days + 1
age_start = (span_start.normalize() - BIRTH_DATE).days if HAS_DOB else None
age_end   = (span_end.normalize() - BIRTH_DATE).days if HAS_DOB else None

print("=" * 70)
print(f"DATA SPAN: {span_start:%Y-%m-%d %H:%M}  ->  {span_end:%Y-%m-%d %H:%M}  ({n_days} days)")
print(f"Records: {len(df)} total | feeds {len(feeds)} | diapers {len(diapers)} | "
      f"sleeps {len(sleeps)} | baths {len(baths)}")
print("=" * 70)

# ---- only analyze full days (drop first & last partial day) ----
all_dates = sorted(df["date"].dropna().unique())
full_dates = all_dates[1:-1]  # drop boundary partial days
fdf = df[df["date"].isin(full_dates)]
ff  = feed_sessions[feed_sessions["date"].isin(full_dates)]
fd  = diapers[diapers["date"].isin(full_dates)]
fs  = sleeps[sleeps["date"].isin(full_dates)]

# ---- daily aggregates ----
daily = pd.DataFrame(index=pd.Index(full_dates, name="date"))
daily["feeds"]        = ff.groupby("date").size()
daily["feed_min"]     = ff.groupby("date")["dur_min"].sum()
daily["diapers"]      = fd.groupby("date").size()
daily["sleep_blocks"] = fs.groupby("date").size()
daily["sleep_min"]    = fs.groupby("date")["dur_min"].sum()
daily = daily.fillna(0)

# poo vs pee classification.
# NOTE: for Diaper rows the contents live in 'End Condition' (e.g. "Both, pee:medium poo:medium",
# "Pee:large", "Poo"). Color is in 'Duration', consistency in 'Start Condition'.
def has(s, kw):
    return isinstance(s, str) and kw in s.lower()
diapers["detail"] = diapers["End Condition"]
diapers["color"]  = diapers["Duration"]
diapers["consistency"] = diapers["Start Condition"]
diapers["poo"] = diapers["detail"].apply(lambda s: has(s, "poo") or has(s, "both"))
diapers["pee"] = diapers["detail"].apply(lambda s: has(s, "pee") or has(s, "both"))
fd2 = diapers[diapers["date"].isin(full_dates)]
daily["poo"] = fd2.groupby("date")["poo"].sum()
daily["pee"] = fd2.groupby("date")["pee"].sum()
daily = daily.fillna(0)

print("\nDAILY AVERAGES (full days only, n={}):".format(len(full_dates)))
print(f"  Feeds/day:           {daily['feeds'].mean():.1f}  (range {int(daily['feeds'].min())}-{int(daily['feeds'].max())})")
print(f"  Feed minutes/day:    {daily['feed_min'].mean():.0f} min  ({daily['feed_min'].mean()/60:.1f} h)")
print(f"  Avg feed length:     {ff['dur_min'].mean():.1f} min  (median {ff['dur_min'].median():.0f})")
print(f"  Diapers/day:         {daily['diapers'].mean():.1f}")
print(f"  Poo diapers/day:     {daily['poo'].mean():.1f}")
print(f"  Logged sleep/day:    {daily['sleep_min'].mean()/60:.1f} h  (in {daily['sleep_blocks'].mean():.1f} logged blocks)")

# ---- feed intervals (time between consecutive feed starts) ----
feeds_sorted = feeds.sort_values("Start")
intervals = feeds_sorted["Start"].diff().dt.total_seconds() / 3600
intervals = intervals[(intervals > 0) & (intervals < 12)]
print(f"\nFEED INTERVALS: median {intervals.median():.1f} h, mean {intervals.mean():.1f} h, "
      f"max gap {intervals.max():.1f} h")

# ---- longest sleep stretch per day (proxy for night consolidation) ----
print(f"\nLONGEST SLEEP BLOCKS (top 5): "
      + ", ".join(f"{m/60:.1f}h" for m in sleeps['dur_min'].nlargest(5)))

# ---- stool consistency / color over time (clinically relevant) ----
poo_d = diapers[diapers["poo"]].copy()
print(f"\nSTOOL: {len(poo_d)} poo diapers over span "
      f"({len(poo_d)/n_days:.1f}/day)")
print("  consistency:", dict(poo_d["consistency"].value_counts()))
print("  color:      ", dict(poo_d["color"].value_counts()))

# ---- breast side balance ----
def side_min(row, side):
    # Start Condition like '00:15R'; End Location/Notes like '00:33L'
    tot = 0
    for col in ["Start Condition", "End Condition", "Notes"]:
        v = row.get(col)
        if isinstance(v, str):
            m = re.match(r"^(\d{2}):(\d{2})" + side + r"$", v.strip())
            if m:
                tot += int(m.group(1)) * 60 + int(m.group(2))
    return tot
L = feeds.apply(lambda r: side_min(r, "L"), axis=1).sum()
R = feeds.apply(lambda r: side_min(r, "R"), axis=1).sum()
print(f"\nBREAST SIDE BALANCE: Left {L} min ({L/(L+R)*100:.0f}%)  |  Right {R} min ({R/(L+R)*100:.0f}%)")

# ===================================================================
#  VISUALIZATION
# ===================================================================
fig = plt.figure(figsize=(16, 18))
gs = fig.add_gridspec(5, 2, height_ratios=[1.1, 1, 1, 1, 0.9], hspace=0.45, wspace=0.22)

day_labels = [d.strftime("%m-%d") for d in full_dates]
x = np.arange(len(full_dates))

# --- Panel 1: 24h activity timeline (swimlane) over full span ---
ax1 = fig.add_subplot(gs[0, :])
type_y = {"Sleep": 0, "Feed": 1, "Diaper": 2, "Bath": 3}
type_c = {"Sleep": "#5B8FF9", "Feed": "#5AD8A6", "Diaper": "#F6BD16", "Bath": "#9270CA"}
base_date = pd.Timestamp(all_dates[0])
for _, r in df.iterrows():
    if pd.isna(r["Start"]):
        continue
    t = r["Type"]
    if t not in type_y:
        continue
    day_off = (r["Start"].normalize() - base_date).days
    hod = r["Start"].hour + r["Start"].minute / 60
    if pd.notna(r["End"]) and pd.notna(r["dur_min"]) and r["dur_min"] > 0:
        end_hod = hod + r["dur_min"] / 60
        # clip to same day for plotting simplicity
        ax1.plot([hod, min(end_hod, 24)], [day_off, day_off], lw=6,
                 color=type_c[t], solid_capstyle="butt", alpha=0.9)
        if end_hod > 24:  # wrap remainder
            ax1.plot([0, end_hod - 24], [day_off + 1, day_off + 1], lw=6,
                     color=type_c[t], solid_capstyle="butt", alpha=0.9)
    else:
        ax1.plot(hod, day_off, "o", color=type_c[t], ms=5)
ax1.set_xlim(0, 24); ax1.set_xticks(range(0, 25, 2))
ax1.set_xlabel("Hour of day")
ax1.set_yticks(range(len(all_dates)))
ax1.set_yticklabels([d.strftime("%a %m-%d") for d in all_dates], fontsize=8)
ax1.invert_yaxis()
ax1.set_title("Daily rhythm — every logged event by hour of day  (shaded = night)", pad=28)
ax1.axvspan(0, 7, color="#1f2540", alpha=0.06)
ax1.axvspan(21, 24, color="#1f2540", alpha=0.06)
ax1.legend(handles=[Patch(color=c, label=t) for t, c in type_c.items()],
           ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.005), frameon=False,
           fontsize=9)

# --- Panel 2: feeds per day + feed minutes ---
ax2 = fig.add_subplot(gs[1, 0])
ax2.bar(x, daily["feeds"], color="#5AD8A6", alpha=0.85)
ax2.axhline(daily["feeds"].mean(), color="#0b6b4f", ls="--", lw=1,
            label=f"avg {daily['feeds'].mean():.1f}")
ax2.set_title("Feeds per day")
ax2.set_xticks(x); ax2.set_xticklabels(day_labels, rotation=60, fontsize=7)
ax2.set_ylabel("breast sessions")
ax2.legend(frameon=False, fontsize=8)

ax2b = fig.add_subplot(gs[1, 1])
ax2b.bar(x, daily["feed_min"] / 60, color="#36A36A", alpha=0.85)
ax2b.axhline((daily["feed_min"]/60).mean(), color="#0b6b4f", ls="--", lw=1,
             label=f"avg {(daily['feed_min']/60).mean():.1f} h")
ax2b.set_title("Time on breast per day")
ax2b.set_xticks(x); ax2b.set_xticklabels(day_labels, rotation=60, fontsize=7)
ax2b.set_ylabel("hours")
ax2b.legend(frameon=False, fontsize=8)

# --- Panel 3: diapers (poo/pee) ---
ax3 = fig.add_subplot(gs[2, 0])
ax3.bar(x, daily["pee"], color="#F6BD16", label="pee (incl. both)", alpha=0.85)
ax3.bar(x, daily["poo"], color="#B07D00", label="poo (incl. both)", alpha=0.9, width=0.5)
ax3.set_title("Diapers per day")
ax3.set_xticks(x); ax3.set_xticklabels(day_labels, rotation=60, fontsize=7)
ax3.set_ylabel("count"); ax3.legend(frameon=False, fontsize=8)

# --- Panel 4: logged sleep hours ---
ax4 = fig.add_subplot(gs[2, 1])
ax4.bar(x, daily["sleep_min"] / 60, color="#5B8FF9", alpha=0.85)
ax4.set_title("Logged sleep per day  (⚠ likely under-recorded)")
ax4.set_xticks(x); ax4.set_xticklabels(day_labels, rotation=60, fontsize=7)
ax4.set_ylabel("hours")

# --- Panel 5: feed-start hour histogram ---
ax5 = fig.add_subplot(gs[3, 0])
ax5.hist(feeds["hour"].dropna(), bins=np.arange(0, 25), color="#5AD8A6",
         edgecolor="white", alpha=0.9)
ax5.set_title("When do feeds start? (hour of day)")
ax5.set_xlabel("hour"); ax5.set_ylabel("count"); ax5.set_xticks(range(0, 25, 3))
ax5.axvspan(0, 7, color="#1f2540", alpha=0.06)
ax5.axvspan(21, 24, color="#1f2540", alpha=0.06)

# --- Panel 6: feed interval distribution ---
ax6 = fig.add_subplot(gs[3, 1])
ax6.hist(intervals, bins=np.arange(0, 8, 0.5), color="#9270CA",
         edgecolor="white", alpha=0.9)
ax6.axvline(intervals.median(), color="#4b2e83", ls="--",
            label=f"median {intervals.median():.1f} h")
ax6.set_title("Gap between feeds")
ax6.set_xlabel("hours between feed starts"); ax6.set_ylabel("count")
ax6.legend(frameon=False, fontsize=8)

# --- Panel 7: feed duration trend (daily mean +/- spread) ---
ax7 = fig.add_subplot(gs[4, 0])
g = ff.groupby("date")["dur_min"]
mean_d = g.mean(); std_d = g.std().fillna(0)
ax7.plot(x, mean_d.reindex(full_dates).values, "-o", color="#36A36A", ms=4)
ax7.fill_between(x, (mean_d - std_d).reindex(full_dates).values,
                 (mean_d + std_d).reindex(full_dates).values,
                 color="#5AD8A6", alpha=0.2)
ax7.set_title("Avg feed length per day (min)")
ax7.set_xticks(x); ax7.set_xticklabels(day_labels, rotation=60, fontsize=7)
ax7.set_ylabel("minutes")

# --- Panel 8: stool consistency over time (clinical flag) ---
ax8 = fig.add_subplot(gs[4, 1])
cons_order = ["Pebbles", "Mucousy", "Loose", "Runny", "Diarrhea"]
cons_color = {"Pebbles": "#8c6d3f", "Mucousy": "#c9a227", "Loose": "#e8b84b",
              "Runny": "#f0863c", "Diarrhea": "#d64545"}
poo_full = poo_d[poo_d["date"].isin(full_dates)]
for ci, cons in enumerate(cons_order):
    sub = poo_full[poo_full["consistency"] == cons]
    xs = [full_dates.index(d) for d in sub["date"] if d in full_dates]
    ax8.scatter(xs, [ci] * len(xs), s=70, color=cons_color[cons], alpha=0.85)
# unlabeled / other consistencies
other = poo_full[~poo_full["consistency"].isin(cons_order)]
xs = [full_dates.index(d) for d in other["date"] if d in full_dates]
ax8.scatter(xs, [len(cons_order)] * len(xs), s=70, color="#999", alpha=0.7)
ax8.set_yticks(range(len(cons_order) + 1))
ax8.set_yticklabels(cons_order + ["(unspec.)"], fontsize=8)
ax8.set_xticks(x); ax8.set_xticklabels(day_labels, rotation=60, fontsize=7)
ax8.set_title("Stool consistency over time")
ax8.grid(True, axis="y", alpha=0.2)

print(f"\nBREAST SIDE BALANCE used in stats only: L {L} / R {R} min")

fig.suptitle(
    f"Newborn tracking dashboard  ·  {span_start:%b %d} – {span_end:%b %d, %Y}  "
    f"·  {len(feeds)} feeds, {len(diapers)} diapers, {len(sleeps)} sleep logs",
    fontsize=15, fontweight="bold", y=0.995)

out = "/home/user/claude-code/baby_analysis/dashboard.png"
fig.savefig(out, bbox_inches="tight", facecolor="white")
print(f"\nSaved -> {out}")

# ===================================================================
#  EXTRA FIGURE: day vs night split + 3-day rolling trends
# ===================================================================
# Night defined as 19:00–07:00 (12h). Tag every feed session.
NIGHT_START, NIGHT_END = 19, 7
def is_night(h):
    return (h >= NIGHT_START) or (h < NIGHT_END)
ff = ff.copy()
ff["night"] = ff["hour"].apply(is_night)

# per-day day/night minutes and counts
dn_min = ff.pivot_table(index="date", columns="night", values="dur_min",
                        aggfunc="sum").reindex(full_dates).fillna(0)
dn_cnt = ff.pivot_table(index="date", columns="night", values="dur_min",
                        aggfunc="count").reindex(full_dates).fillna(0)
night_min = dn_min.get(True, pd.Series(0, index=full_dates))
day_min   = dn_min.get(False, pd.Series(0, index=full_dates))
night_cnt = dn_cnt.get(True, pd.Series(0, index=full_dates))
day_cnt   = dn_cnt.get(False, pd.Series(0, index=full_dates))

tot_night = ff[ff["night"]]["dur_min"].sum()
tot_day   = ff[~ff["night"]]["dur_min"].sum()
pct_night = tot_night / (tot_night + tot_day) * 100
print("\n" + "=" * 70)
print(f"DAY vs NIGHT (night = {NIGHT_START}:00–0{NIGHT_END}:00, 12h window)")
print(f"  Feed minutes:  day {tot_day:.0f}  |  night {tot_night:.0f}  "
      f"({pct_night:.0f}% of breast-time is at night)")
print(f"  Feeds/night avg: {night_cnt.mean():.1f}  |  Feeds/day avg: {day_cnt.mean():.1f}")
print(f"  Night is 12h of 24h, so a flat distribution = 50%; "
      f"observed {pct_night:.0f}%.")

# rolling 3-day means
roll = pd.DataFrame({
    "feeds": daily["feeds"],
    "feed_h": daily["feed_min"] / 60,
    "diapers": daily["diapers"],
    "poo": daily["poo"],
}, index=pd.Index(full_dates))
roll3 = roll.rolling(3, center=True, min_periods=1).mean()

fig2 = plt.figure(figsize=(16, 9))
gs2 = fig2.add_gridspec(2, 2, hspace=0.42, wspace=0.2)

# Panel A: stacked day/night feed minutes
axA = fig2.add_subplot(gs2[0, 0])
axA.bar(x, day_min.values / 60, color="#5AD8A6", label="day (07–19)", alpha=0.9)
axA.bar(x, night_min.values / 60, bottom=day_min.values / 60,
        color="#3b5b8c", label="night (19–07)", alpha=0.9)
axA.set_title("Feed time per day, split day vs night")
axA.set_xticks(x); axA.set_xticklabels(day_labels, rotation=60, fontsize=7)
axA.set_ylabel("hours on breast"); axA.legend(frameon=False, fontsize=8)

# Panel B: % of feed-time at night (trend)
axB = fig2.add_subplot(gs2[0, 1])
pct_series = (night_min / (night_min + day_min) * 100).reindex(full_dates)
axB.plot(x, pct_series.values, "-o", color="#3b5b8c", ms=4)
axB.axhline(50, color="#999", ls="--", lw=1, label="50% (flat day/night)")
axB.axhline(pct_series.mean(), color="#d64545", ls=":", lw=1.2,
            label=f"avg {pct_series.mean():.0f}%")
axB.set_title("Share of daily breast-time happening at night")
axB.set_xticks(x); axB.set_xticklabels(day_labels, rotation=60, fontsize=7)
axB.set_ylabel("% of feed minutes"); axB.set_ylim(0, 70)
axB.legend(frameon=False, fontsize=8)

# Panel C: 3-day rolling feeds + diapers
axC = fig2.add_subplot(gs2[1, 0])
axC.plot(x, roll["feeds"].values, color="#5AD8A6", alpha=0.35, lw=1, label="feeds (raw)")
axC.plot(x, roll3["feeds"].values, color="#1f7a55", lw=2.5, label="feeds (3-day)")
axC.plot(x, roll["diapers"].values, color="#F6BD16", alpha=0.35, lw=1, label="diapers (raw)")
axC.plot(x, roll3["diapers"].values, color="#9a7400", lw=2.5, label="diapers (3-day)")
axC.set_title("3-day rolling trend — feeds & diapers per day")
axC.set_xticks(x); axC.set_xticklabels(day_labels, rotation=60, fontsize=7)
axC.set_ylabel("count / day"); axC.legend(frameon=False, fontsize=8, ncol=2)

# Panel D: 3-day rolling feed hours + poo
axD = fig2.add_subplot(gs2[1, 1])
axD.plot(x, roll["feed_h"].values, color="#36A36A", alpha=0.35, lw=1, label="feed h (raw)")
axD.plot(x, roll3["feed_h"].values, color="#0b6b4f", lw=2.5, label="feed h (3-day)")
axD.plot(x, roll["poo"].values, color="#B07D00", alpha=0.35, lw=1, label="poo (raw)")
axD.plot(x, roll3["poo"].values, color="#7a5600", lw=2.5, label="poo (3-day)")
axD.set_title("3-day rolling trend — breast hours & poo diapers per day")
axD.set_xticks(x); axD.set_xticklabels(day_labels, rotation=60, fontsize=7)
axD.set_ylabel("hours / count per day"); axD.legend(frameon=False, fontsize=8, ncol=2)

fig2.suptitle("Day/night split & 3-day rolling trends", fontsize=15,
              fontweight="bold", y=0.98)
out2 = "/home/user/claude-code/baby_analysis/trends.png"
fig2.savefig(out2, bbox_inches="tight", facecolor="white")
print(f"Saved -> {out2}")

# ===================================================================
#  SELF-CONTAINED HTML REPORT (images embedded as base64)
# ===================================================================
import base64

def b64(path):
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()

stat_rows = [
    ("Data span", f"{span_start:%b %d} – {span_end:%b %d, %Y} ({n_days} days)"),
    ("Baby's age over span", f"day {age_start} – day {age_end} of life "
        f"(DOB {BIRTH_DATE:%b %d, %Y})" if HAS_DOB else "—"),
    ("Total records", f"{len(df)} ({len(feeds)} feeds, {len(diapers)} diapers, "
                      f"{len(sleeps)} sleeps, {len(baths)} baths)"),
    ("Feeds / day", f"{daily['feeds'].mean():.1f} (range {int(daily['feeds'].min())}–{int(daily['feeds'].max())})"),
    ("Time on breast / day", f"{daily['feed_min'].mean()/60:.1f} h"),
    ("Avg feed length", f"{ff['dur_min'].mean():.1f} min (median {ff['dur_min'].median():.0f})"),
    ("Median gap between feeds", f"{intervals.median():.1f} h (max {intervals.max():.1f} h)"),
    ("Breast-time at night (19–07)", f"{pct_night:.0f}%"),
    ("Diapers / day", f"{daily['diapers'].mean():.1f}"),
    ("Poo / day", f"{daily['poo'].mean():.1f} (yellow {(poo_d['color']=='yellow').sum()}, "
                  f"green {(poo_d['color']=='green').sum()})"),
    ("Logged sleep / day", f"{daily['sleep_min'].mean()/60:.1f} h ⚠ under-recorded"),
    ("Breast side balance", f"L {L/(L+R)*100:.0f}% / R {R/(L+R)*100:.0f}%"),
]
rows_html = "\n".join(
    f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in stat_rows)

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Newborn tracking report · {span_start:%b %d}–{span_end:%b %d %Y}</title>
<style>
  :root {{ --green:#1f7a55; --ink:#1f2540; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
          color:var(--ink); max-width:1100px; margin:0 auto; padding:32px 20px 80px;
          line-height:1.5; background:#fafbfc; }}
  h1 {{ font-size:1.7rem; margin:0 0 4px; }}
  .sub {{ color:#667; margin-bottom:28px; }}
  h2 {{ border-bottom:2px solid #e3e7ec; padding-bottom:6px; margin-top:40px; }}
  table {{ border-collapse:collapse; width:100%; margin:8px 0 4px; font-size:0.95rem; }}
  th,td {{ text-align:left; padding:8px 10px; border-bottom:1px solid #e8ecf0; }}
  th {{ width:42%; color:#445; font-weight:600; background:#f3f6f9; }}
  img {{ width:100%; height:auto; border:1px solid #e3e7ec; border-radius:8px;
         margin:10px 0; background:#fff; }}
  .flags li {{ margin:6px 0; }}
  .warn {{ color:#b3261e; }} .ok {{ color:var(--green); }}
  .note {{ font-size:0.85rem; color:#778; margin-top:40px; border-top:1px solid #e3e7ec;
           padding-top:16px; }}
  ul {{ padding-left:20px; }}
</style></head><body>
<h1>Newborn tracking — critical analysis</h1>
<div class="sub">{span_start:%B %d} – {span_end:%B %d, %Y} · first {age_end} days of life
(DOB {BIRTH_DATE:%B %d, %Y}) · {len(df)} logged events</div>

<h2>Key numbers</h2>
<table>{rows_html}</table>

<h2>What the data says</h2>
<ul class="flags">
  <li class="ok"><b>Feeding is intense &amp; cluster-heavy.</b> ~{daily['feeds'].mean():.0f} feeds/day,
      median gap {intervals.median():.1f} h, median session {ff['dur_min'].median():.0f} min — normal newborn cluster feeding.</li>
  <li class="ok"><b>Stool looks reassuring.</b> mostly yellow ({(poo_d['color']=='yellow').sum()} yellow vs
      {(poo_d['color']=='green').sum()} green), ~{daily['poo'].mean():.1f}/day.</li>
  <li><b>Night load:</b> {pct_night:.0f}% of breast-time happens in the 19:00–07:00 window
      (a flat clock would be 50%) — feeding is still round-the-clock with no night consolidation yet.</li>
  <li class="warn"><b>Sleep is under-logged</b> ({daily['sleep_min'].mean()/60:.1f} h/day vs the expected 14–17 h) —
      treat the sleep panel as a record of logging effort, not actual sleep.</li>
  <li class="warn"><b>Diapers may be under-counted</b> ({daily['diapers'].mean():.1f}/day is on the low side for
      a breastfed newborn) — wet-diaper count is the usual intake check, so worth logging consistently.</li>
</ul>

<h2>Dashboard</h2>
<img src="data:image/png;base64,{b64(out)}" alt="dashboard">

<h2>Day/night split &amp; 3-day rolling trends</h2>
<img src="data:image/png;base64,{b64(out2)}" alt="trends">

<div class="note">
  Generated by <code>analyze.py</code>. Night window = 19:00–07:00. Daily averages use the
  {len(full_dates)} fully-logged days (first/last partial days excluded). This is pattern-reading on
  self-logged data, not medical advice — the sleep and diaper gaps mean the picture is incomplete.
</div>
</body></html>"""

# ===================================================================
#  AGE AXIS  (true age-in-weeks; DOB known)
# ===================================================================
if HAS_DOB:
    study_day = [(pd.Timestamp(d) - BIRTH_DATE).days for d in full_dates]  # age in days
    week_idx  = [a // 7 + 1 for a in study_day]   # week-of-life: days 0-6 -> wk1
    top_label = f"age in days  (DOB {BIRTH_DATE:%b %d, %Y})"
    daytick   = [f"d{a}" for a in study_day]
else:
    day0 = full_dates[0]
    study_day = [(d - day0).days + 1 for d in full_dates]
    week_idx  = [(sd - 1) // 7 + 1 for sd in study_day]
    top_label = "study day (Day 1 = first full log)"
    daytick   = [f"D{sd}" for sd in study_day]

def week_range_label(w):
    """Age-day range covered by week-of-life w within the full-day set."""
    ages = [study_day[i] for i in range(len(full_dates)) if week_idx[i] == w]
    return f"d{min(ages)}–{max(ages)}"

# add a secondary age axis + week-of-life shading to the trends figure
week_colors = ["#eef4ff", "#fff7e8", "#f0fff4"]
for ax in (axA, axB, axC, axD):
    for i, sd in enumerate(study_day):
        ax.axvspan(i - 0.5, i + 0.5, color=week_colors[(week_idx[i]-1) % 3],
                   alpha=0.5, zorder=0)
    top = ax.secondary_xaxis("top")
    top.set_xticks(x)
    top.set_xticklabels(daytick, fontsize=6, color="#667")
    top.set_xlabel(top_label, fontsize=8, color="#667")
fig2.savefig(out2, bbox_inches="tight", facecolor="white")
print(f"Re-saved with age axis -> {out2}")

# ===================================================================
#  WEEK 1 vs WEEK 2 SUMMARY
# ===================================================================
wk_of_date = {d: week_idx[i] for i, d in enumerate(full_dates)}
ff["wk"]  = ff["date"].map(wk_of_date)
fd2["wk"] = fd2["date"].map(wk_of_date)
poo_d_full = poo_d[poo_d["date"].isin(full_dates)].copy()
poo_d_full["wk"] = poo_d_full["date"].map(wk_of_date)

# feed intervals per week
fs_sorted = feeds.copy()
fs_sorted["d"] = fs_sorted["Start"].dt.date
fs_sorted = fs_sorted[fs_sorted["d"].isin(full_dates)].sort_values("Start")
fs_sorted["gap_h"] = fs_sorted["Start"].diff().dt.total_seconds() / 3600
fs_sorted["wk"] = fs_sorted["d"].map(wk_of_date)

weeks_present = sorted(set(week_idx))
wk_rows = []
for w in weeks_present:
    days = [d for d in full_dates if wk_of_date[d] == w]
    nd = len(days)
    fw = ff[ff["wk"] == w]
    dw = fd2[fd2["wk"] == w]
    pw = poo_d_full[poo_d_full["wk"] == w]
    gaps = fs_sorted[(fs_sorted["wk"] == w)]["gap_h"]
    gaps = gaps[(gaps > 0) & (gaps < 12)]
    nightmin = fw[fw["night"]]["dur_min"].sum()
    allmin = fw["dur_min"].sum()
    wlabel = (f"Week {w} of life ({week_range_label(w)})" if HAS_DOB
              else f"Week {w}")
    wk_rows.append({
        "Week": wlabel + (" *" if nd < 7 else ""),
        "Days": nd,
        "Feeds/day": fw.shape[0] / nd,
        "Breast h/day": fw["dur_min"].sum() / 60 / nd,
        "Avg feed (min)": fw["dur_min"].mean(),
        "Median gap (h)": gaps.median(),
        "% night": nightmin / allmin * 100 if allmin else np.nan,
        "Diapers/day": dw.shape[0] / nd,
        "Poo/day": pw.shape[0] / nd,
        "% green stool": (pw["color"] == "green").mean() * 100 if len(pw) else 0,
    })
wk_df = pd.DataFrame(wk_rows).set_index("Week")

print("\n" + "=" * 70)
print("WEEKLY SUMMARY  (week-of-life; DOB {:%b %d, %Y})".format(BIRTH_DATE)
      if HAS_DOB else "WEEKLY SUMMARY (Day 1 = first full log)")
print(wk_df.round(1).to_string())

# delta Week1 -> Week2 (only if both full)
if len(weeks_present) >= 2:
    w1, w2 = wk_df.iloc[0], wk_df.iloc[1]
    print("\nWeek 1 -> Week 2 change:")
    for col in ["Feeds/day", "Breast h/day", "Avg feed (min)", "Median gap (h)",
                "% night", "Diapers/day", "Poo/day"]:
        d = w2[col] - w1[col]
        print(f"  {col:16s} {w1[col]:6.1f} -> {w2[col]:6.1f}  ({d:+.1f})")

# ---- weekly comparison figure (grouped bars) ----
metrics = ["Feeds/day", "Breast h/day", "Avg feed (min)", "Median gap (h)",
           "% night", "Diapers/day", "Poo/day"]
fig3, axes3 = plt.subplots(2, 4, figsize=(16, 7))
axes3 = axes3.ravel()
bar_colors = ["#5AD8A6", "#5B8FF9", "#F6BD16"]
short_labels = ([f"Wk {w}\n({week_range_label(w)})" for w in weeks_present] if HAS_DOB
                else [f"Week {w}" for w in weeks_present])
short_labels = [l + " *" if d < 7 else l
                for l, d in zip(short_labels, wk_df["Days"].values)]
for ax, m in zip(axes3, metrics):
    vals = wk_df[m].values
    labels = short_labels
    bars = ax.bar(labels, vals, color=[bar_colors[i % 3] for i in range(len(vals))],
                  alpha=0.9)
    ax.set_title(m, fontsize=11)
    ax.tick_params(axis="x", labelsize=8)
    for b, v in zip(bars, vals):
        if not np.isnan(v):
            ax.text(b.get_x() + b.get_width()/2, v, f"{v:.1f}",
                    ha="center", va="bottom", fontsize=8)
    ax.margins(y=0.18)
# last axis: hide if unused
for ax in axes3[len(metrics):]:
    ax.axis("off")
axes3[-1].axis("off")
axes3[-1].text(0.0, 0.9,
               f"Weeks of life from DOB {BIRTH_DATE:%b %d, %Y}\n"
               "(week 1 = days 0–6, etc.).\n"
               "* = partial week (fewer than 7 days\n"
               "of full logging).\n\n"
               "Birth day (d0) and the final partial\n"
               "day are excluded from daily averages.",
               fontsize=9, va="top", color="#445")
fig3.suptitle("Week-over-week comparison (age in weeks of life)",
              fontsize=15, fontweight="bold", y=1.0)
fig3.tight_layout(rect=[0, 0, 1, 0.97])
out4 = "/home/user/claude-code/baby_analysis/weekly.png"
fig3.savefig(out4, bbox_inches="tight", facecolor="white")
print(f"Saved -> {out4}")

# ---- weekly table as HTML ----
wk_html = wk_df.round(1).reset_index().to_html(index=False, border=0,
            classes="wk", float_format=lambda v: f"{v:.1f}")

out3 = "/home/user/claude-code/baby_analysis/report.html"
# inject weekly section + extra image into the HTML built earlier
weekly_section = f"""
<h2>Week-over-week (age in weeks of life)</h2>
<table class="wk-wrap">{wk_html}</table>
<img src="data:image/png;base64,{b64(out4)}" alt="weekly comparison">
<p class="sub" style="margin-top:6px">Age computed from <b>DOB {BIRTH_DATE:%B&nbsp;%d,&nbsp;%Y}</b>
(same day tracking began). Week 1 = days&nbsp;0–6 of life, etc. * marks a partial week.
The birth day and the final partial day are excluded from daily averages.</p>
"""
html = html.replace("<h2>Dashboard</h2>", weekly_section + "\n<h2>Dashboard</h2>")
# re-embed trends image (now has study-day axis)
html = re.sub(r'(<h2>Day/night split[^<]*</h2>\s*<img src="data:image/png;base64,)[^"]+',
              lambda mobj: mobj.group(1) + b64(out2), html)
# small style for the weekly table
html = html.replace("</style>",
    "  table.wk {{ font-size:0.85rem; }} table.wk th {{ background:#eef4ff; width:auto; }}\n</style>"
    .replace("{{","{").replace("}}","}"))
with open(out3, "w") as fh:
    fh.write(html)
print(f"Saved -> {out3}")
