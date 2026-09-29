# Server Monitoring

A collection of lightweight server health-check scripts that report status via
Discord. Each script is designed to be run from cron and exit non-zero when a
problem is detected, so pointing cron/systemd at them gives you alerting with
little setup.

All scripts log to `/var/log/<name>.log` and, when a `notify-discord`
executable is on `PATH`, post a summary message to Discord. The `notify-discord`
binary is a separate small helper (e.g. a wrapper around a Discord webhook) that
this project shells out to — see `_discord.py`.

## Scripts

| Script | What it checks | Exit non-zero when |
|---|---|---|
| `smart-status-all` | SMART health of every detected disk | any disk fails its SMART health check |
| `smart-short-all` | SMART short self-test on every disk (parallel) | any disk fails its self-test |
| `check-free-space` | Free space on every mounted fs + zpool vs alert limits | any device is below its free-space limit |
| `disk-utilization-gatherer` | Samples per-disk util% with `iostat`, appends CSV (`ts,dev,util`) | iostat fails |
| `disk-utilization` | Analyzes log written by the gatherer (min/avg/max/median) | a device is at/below WARNING/CRITICAL util |
| `check-memory-fragmentation` | Worst-case memory fragmentation index | fragmentation >= WARN/ERR threshold |
| `dmesg-check-errors` | `dmesg --level=err+` since 1 day ago (with ignore list) | any non-ignored kernel error lines |

## Requirements

- Python 3.10+
- `tabulate` (optional — degrades to tab-separated output)
- `smartctl` (smartmontools) for the SMART scripts
- `partx`/`findmnt` for `disk-utilization` device naming
- `zpool` only if you use ZFS
- `iostat` (sysstat) for `disk-utilization-gatherer`

```bash
pip install -r requirements.txt
```

## Settings

Optional `settings.json` (see `settings.json.example`) supports per-path alert
overrides and excluded paths, consumed by `check-free-space`:

```json
{
  "CUSTOM_ALERT_LIMITS": { "/boot": 200000 },
  "EXCLUDE_PATHS": ["/.snapshots"]
}
```

Limits are in bytes; the default alert limit is 50 GiB of free space. Log paths
for the disk-utilization scripts can be redirected with `DISK_UTILIZATION_LOG_DIR`.

## Crontab examples

```cron
*/10 * * * * /opt/server-monitoring/check-free-space
0 3 * * *  /opt/server-monitoring/smart-status-all
0 4 * * 1  /opt/server-monitoring/smart-short-all
*/15 * * *  /opt/server-monitoring/disk-utilization-gatherer
*/30 * * *  /opt/server-monitoring/disk-utilization
*/15 * * *  /opt/server-monitoring/dmesg-check-errors
```

## Development

```bash
python -m pytest tests/ -v
ruff check .
```