---
name: vps-server-management
description: Rent, secure, configure, and operate Linux VPS servers, and deploy applications onto them. Use for VPS, аренда сервера, арендованный сервер, SSH-ключи, вход по ключу, настройка сервера, Ubuntu server hardening, firewall/ufw, swap, PostgreSQL on a server, reverse proxy, HTTPS/Let's Encrypt, deploying a FastAPI/web app, nginx/Caddy, systemd services, server backups, and connecting to a server from Windows.
---

# VPS Server Management

## Core Goal

Take a rented Linux VPS from bare login to a secure, running application server, and keep operating it: access, hardening, the app stack, HTTPS, backups. Encode the user's environment and preferences once so each new server does not re-derive them. For the application data model and stack choices, defer to `database-development`; this skill owns the server/ops layer.

## User Environment (durable)

The user works from **Windows** with a **VPN** (AmneziaWG-based). This shapes every connection task:

- **Use the native Windows OpenSSH client** `C:\Windows\System32\OpenSSH\ssh.exe` (and `scp.exe`). It connects reliably here.
- **Do NOT use PuTTY `plink.exe`.** Over this user's VPN it fails at the SSH handshake with `FATAL ERROR: Network error: Software caused connection abort`, even when native `ssh` to the same host works. `plink -pw <password>` for scripted password login is therefore unavailable.
- **The route to a server may work only via VPN, or only bypassing it — diagnose, don't assume.** Test each path with `Test-NetConnection <ip> -Port 22` and `tracert`; some Russian VPS are unreachable from the local ISP entirely (VPN is the only path), while shared VPN exits get port 22 throttled. The Amnezia split-tunnel list works only when its master toggle is ON and after a VPN reconnect. Full decision guide: `references/connection-lessons.md`.
- **Prefer a non-standard SSH port (e.g. 2222) on new servers.** Port 22 from shared/VPN IPs gets anti-brute-force filtering (TCP connects, banner exchange times out), and bots hammer 22 constantly. On Ubuntu 24.04 the port change requires disabling `ssh.socket` (socket activation), not just editing `sshd_config`.
- Because `ssh.exe` reads the password from the console (not stdin), the **one-time key install cannot be automated** from a background shell. Have the user run that single command in their own PowerShell window; everything afterward runs non-interactively via key auth.

See `references/connection-lessons.md` for the full troubleshooting log; append new environment quirks there.

## Access: SSH keys first

1. Generate a keypair on the user's PC if absent: `ssh-keygen -t ed25519 -C "<pc-name>"` (no passphrase unless the user asks). Private key never leaves the PC.
2. Install the public key on the server. First time needs the password, so the user runs it once interactively:
   ```powershell
   Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub" | ssh -o StrictHostKeyChecking=accept-new root@<ip> "mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys; chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys; echo DONE"
   ```
3. Verify from a background shell: `ssh -o BatchMode=yes root@<ip> "echo OK"` — key auth is non-interactive, so all later automation works.
4. **Do not disable password authentication unless the user explicitly asks.** This user values transparency and simplicity and asked to keep password login working (2026-07-20). Recommend a strong password and provider-panel password rotation instead of forcing key-only.

## Secrets Handling

- Never write server IPs, passwords, or private keys into the skill, into Git, or into vault notes that sync. Keep them only where the user put them (provider panel) or in an ignored local file.
- If the user pastes a server password into chat, note that it now lives in history and suggest rotating it in the provider panel; do not echo it back into files.

## Initial Server Setup (Ubuntu LTS)

Run in order over `ssh`, explaining each step (the user is learning):

1. `apt update && apt -y upgrade` — patch the system.
2. Swap (important on 1 GB RAM boxes): create a swapfile so the box does not OOM under PostgreSQL + app.
   ```bash
   fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
   echo '/swapfile none swap sw 0 0' >> /etc/fstab
   ```
3. Firewall with `ufw`: allow OpenSSH and the web ports, then enable.
   ```bash
   ufw allow OpenSSH && ufw allow 80 && ufw allow 443 && ufw --force enable
   ```
4. Timezone/locale as needed; a non-root sudo user if the user wants one (optional — keep it simple by default).

## Application Stack

Follow `database-development` for the app's data model and default stack. On the server that means, by default:

- **PostgreSQL** bound to `localhost` only (never expose 5432 to the internet); the app connects as a least-privilege DB user.
- The app (e.g. **FastAPI + uvicorn**) run as a **systemd service** so it restarts on crash/reboot; keep the unit file and any compose files in the project repo's `deploy/` folder.
- **Reverse proxy for HTTPS**: Caddy (automatic Let's Encrypt) is the simplest; nginx + certbot is the alternative. No plain-HTTP logins. HTTPS needs a real domain pointed at the server IP.
- Deploy code by `git pull` on the server (or `scp` for small trees); never edit live files by hand without committing.

## Backups (from day one)

- Nightly `pg_dump` to a dated file, plus a copy **off the server** (object storage or a synced drive). A backup that only lives on the same VPS is not a backup.
- Automate with a `cron` job or systemd timer; keep the script in the repo.
- **Test a restore** before declaring backups done.
- **`chmod +x` the scripts in the deploy step, not just once by hand.** Git does not reliably carry the exec bit from a Windows client to a Linux server; a later `git pull`/`reset --hard` can leave `backup.sh` as `-rw-r--r--`. systemd then fails the unit with `status=203/EXEC` and **backups silently stop** — the app keeps working, nobody notices. Real case: two weeks with no backup while the client entered 63 records. Put `chmod +x deploy/*.sh` inside `update.sh`, and also mark them executable in the index: `git update-index --chmod=+x deploy/*.sh`.
- **Check timer health whenever you touch the server**, it costs one command:
  `systemctl list-timers --no-pager | grep <name>` (is it scheduled?) and
  `systemctl status <name>.service --no-pager | head -5` (did the last run succeed?).
  A failed oneshot service leaves no trace in the app — only in `systemctl status`.

## Learning

Before nontrivial server work, read `references/connection-lessons.md`. Afterward, use the `skill-learning` policy to append compact reusable lessons there (environment quirks, provider gotchas, command recipes) — never secrets, IPs, passwords, keys, or one-off project facts.

## Self-Improvement And Publishing

When VPS work reveals a durable, reusable lesson, use the `skill-learning` policy. Save compact rules, command recipes, or environment quirks in this shared-base skill or `references/connection-lessons.md`. Do not store secrets, server IPs, passwords, private keys, connection strings, generated logs, or one-off project facts in the skill.

Before materially editing this skill, applying self-learning updates, or publishing changes, run the owning repository's freshness check: fetch `origin main`, compare local `HEAD` with `origin/main`, fast-forward if local is behind and the relevant working tree is clean, and inspect dirty/ahead/diverged states before continuing.

After materially updating this skill, validate the shared base and adapters when feasible, then commit and push the relevant skill changes to the owning repository by default unless the user explicitly says not to. Stage only relevant skill files and repository metadata. Split commits by semantic block when the update contains independent concerns; avoid vague rollups such as "skill update".

If publishing encounters remote changes or merge conflicts, resolve them autonomously when the intended final meaning can be determined from the files, commit history, nearby rules, and the user's instruction. Preserve compatible rules from both sides, consolidate duplicates, rerun validation, commit the resolved result, and push. Stop only when resolution would require guessing unavailable technical meaning, exposing protected content, discarding user work, or using unavailable repository permissions.

## Общая машина: мышь возвращать туда, откуда взял

Работа идёт за тем же компьютером, за которым в этот же момент сидит человек.
Если для дела понадобилось двигать указатель — запомнить его положение **до
первого движения** и вернуть на то же место, закончив; не в конце всей задачи, а
в конце каждого захода к мыши. То же с передним планом: окно, выведенное наверх
силой, обязано уступить обратно тому, что было впереди.

Подробнее и о том, что из этого следует для замеров с экрана —
`_base/skills/_shared/shared-machine-etiquette.md`.
