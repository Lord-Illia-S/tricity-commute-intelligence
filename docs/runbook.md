# Runbook: poller stopped or VM down

What to do when live data stops arriving. All commands run on the VM, as the `ubuntu` user.

## 1. How to notice

- The heartbeat runs every night at 01:15 and checks yesterday's data (UTC day) in R2.
- Read its log: `tail ~/heartbeat.log`
- A healthy run prints one line per feed with its row count, for `gdansk`, `gdansk_trip_updates` and `gdynia`.
- `ALERT: <feed> has 0 rows on <date>` means that feed uploaded nothing that day. Go to step 2.

## 2. How to check

```bash
docker ps                                # is tci-poller "Up"? "Restarting" or missing = problem
docker logs --tail 30 tci-poller         # the last errors from the poller
ls ~/tci-data/raw/gdansk/$(date -u +%Y%m%d) | tail -3   # newest files (also check gdansk_trip_updates, gdynia)
tail ~/upload.log                        # errors from the hourly upload (empty = fine)
crontab -l                               # upload_hourly at minute 5, heartbeat at 01:15
```

- Container **Up** and fresh files, but an ALERT: the upload is failing. Check `~/upload.log` and the `.env` file.
- Container **Restarting** or **Exited**: the poller crashes. The logs tell you why.
- If you can't SSH into the VM at all, the VM is down. Restart it from the Oracle Cloud console, then come back to step 2.

## 3. How to restart

The container has `--restart unless-stopped`, so it comes back by itself after a VM reboot. If it doesn't, or you changed code:

```bash
cd ~/tricity-commute-intelligence
git checkout main && git pull            # the VM only runs main
docker build -t tci-poller .
docker rm -f tci-poller
docker run -d --name tci-poller --restart unless-stopped -v ~/tci-data:/app/data tci-poller
docker ps                                # should say "Up"
```

The `-v` mount keeps all data in `~/tci-data`, so this is safe. Never delete `~/tci-data` or anything in R2.

## 4. How to catch up

- `upload_hourly` uploads every finished hour it still finds on disk, not just the last one. After a fix, the next run (minute 5 of every hour) uploads anything it missed.
- To catch up right away, run the same command the crontab uses (copy it from `crontab -l`).
- Data that was never polled while the poller was down **can't be recovered**. Write the gap (date and hours) in the PR or the team chat so the analysis can skip it.
