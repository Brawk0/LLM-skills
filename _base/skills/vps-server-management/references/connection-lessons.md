# Connection Lessons (Windows + VPN)

Durable, reusable troubleshooting for connecting to VPS servers from this user's Windows + AmneziaWG VPN setup. No secrets, IPs, or passwords here — environment behavior only.

## Which path reaches the server? Diagnose BEFORE assuming

The user's traffic to a server can go two ways: through the VPN exit, or directly via the local ISP (when the IP is in the VPN's split-tunnel exclusion list). **Neither path is universally right — test both.**

- Через VPN: TCP may connect but SSH may be throttled (see port-22 lesson below).
- Напрямую: some servers are **not routable at all from the local ISP** — `tracert` shows `Request timed out` on every hop and TCP never establishes. For such servers the VPN is the ONLY working path; excluding the IP from the VPN makes things worse, not better.

Diagnostic pair, run per path:

```powershell
Test-NetConnection <ip> -Port 22   # TcpTestSucceeded?
tracert -d -h 5 -w 800 <ip>        # where do packets die?
```

`PingSucceeded: False` alone is normal (many VPS drop ICMP). TCP True + SSH banner timeout = mid-path filtering, NOT a dead server.

## Amnezia split tunneling: the list does nothing until the master toggle is ON

The split-tunnel address list is applied only when the **Split tunneling master switch** (top-right toggle) is enabled, and routes apply only after **reconnecting** the VPN. A filled list under a grey/off toggle silently changes nothing — symptoms then look "intermittent". When split-tunnel behavior seems inconsistent, screenshot-check the toggle state first.

## Port 22 is throttled on shared VPN exits — move SSH to a non-standard port

Symptom: TCP to :22 connects, but SSH dies with `Connection timed out during banner exchange`, while the provider's VNC console shows a healthy, idle server and `journalctl -u ssh` shows **no trace of our attempts** (packets filtered before sshd). Root cause: anti-brute-force filtering of port 22 traffic from shared/VPN IPs (server logs show constant bot password-guessing from the internet — that is what the filters exist for).

Fix: move sshd to a non-standard port (e.g. 2222). Bonus: the bot brute-force noise stops entirely. On **Ubuntu 24.04 the port lives behind socket activation** — editing `sshd_config` alone does nothing while `ssh.socket` holds :22 (`ss -tlnp` shows `("systemd",pid=1,...)` next to sshd). Required sequence:

1. In `/etc/ssh/sshd_config`: `#Port 22` → `Port 2222`.
2. `systemctl disable --now ssh.socket`
3. `systemctl restart ssh`
4. Verify with `ss -tln` → `0.0.0.0:2222`.

Client side afterwards: `ssh -p 2222 root@<ip>`.

## SSH throttling can be per-PROTOCOL and per-source-IP, not per-port

After moving sshd to a non-standard port, the same `banner exchange timeout` on the new port means the filter recognizes the SSH protocol itself (DPI on the banner), keyed to the **source IP** (a shared VPN exit that got flagged — retry storms accelerate this). Definitive test: `journalctl -u ssh --no-pager -n 8` on the server (via provider console or via a sibling server) right after a client attempt. **No log entry means the packets are filtered before sshd** and nothing on the server will fix it. Log entries are NOT an all-clear, though: when the filter drops the server's reply instead of the client's request, the attempts arrive, sshd logs `kex_exchange_identification: Connection closed by remote host`, and the client still sees a banner timeout. Either way the host is innocent — check that its load is zero and your own rate-limit DROP counters are untouched before touching anything. Working fix: change the VPN server/location (new exit IP). Port change is still worth keeping — it silences bot brute-force noise.

## Driving the provider noVNC console programmatically (via browser JS)

When the user logs the provider panel in inside the assistant's browser pane, the noVNC page exposes a global `rfb` object; `rfb.sendKey(keysym, down)` injects keys straight into the VNC protocol — the only reliable input path (synthetic DOM typing does not reach the canvas; the panel's Paste clipboard mangles input).

- **QEMU drops the implicit Shift of keysyms**: sending `>` yields `.`, `#`→`3`, `_`→`-`, `|`→`\` (this is the root cause of all console mangling). Fix: for shifted symbols send `sendKey(0xFFE1,1)` (Shift down) → base-key keysym (`.` for `>`, `3` for `#`, `-` for `_`, `\` for `|`, etc.) → `sendKey(0xFFE1,0)`.
- **Uppercase letters**: send their own keysym directly (works); do NOT wrap lowercase in Shift (stays lowercase).
- Enter = keysym `0xFF0D`. Verify every command by screenshot BEFORE relying on its effect; echo-probe the risky symbols first.
- `window`-attached helpers (`vncType`) disappear on page reload — redefine per call or check existence.
- **Long commands get truncated**: ~200-char strings lose tail characters in flight. Keep each console command under ~100 chars, split chained commands, and screenshot-verify the typed line before trusting the result. An Enter can also get lost — if the screen freezes on a typed line, resend keysym 0xFF0D alone.

## When SSH from the workstation is impossible: console-only operation

A server can be fully set up and deployed with NO working SSH from the workstation: the provider console (driven via `rfb.sendKey`) executes commands, and the **server's own outbound internet** does the heavy lifting — `git clone` from GitHub delivers the code (no SCP needed), apt pulls from the mirror. Check outbound first: `curl -sm 8 -o /dev/null -w code:%{http_code} <url>` against the mirror and github.com. For private GitHub repos use a server-side deploy key. Sed one-liners with `s+old+new+g` (no quotes, no spaces) are the console-safest file edits; beware partial hostname replacements leaving prefixes like `ru.` — verify with `grep` after.

## Port migration safety

Multiple `Port` directives across `sshd_config` and `sshd_config.d/*.conf` make sshd listen on ALL of them — during a port move this is a feature: keep 22+2222 both listening until the new port is confirmed from the client, then optionally remove 22.

## Do not hammer a throttled port

Retry loops against a filtered/throttled SSH port make the filtering worse and pollute the picture. After 2 failures, stop and change the diagnosis (path test, VNC console, different port) instead of retrying harder. One careful attempt per hypothesis.

## Provider VNC (noVNC) console quirks

- **Symbol mangling**: `|` comes out as `\`, `>` gets silently swallowed — both when typed and via the Paste clipboard button. Any command containing pipes or redirects will be corrupted. Compose console commands with NO `|`, `>`, `>>`.
- Workarounds: edit files with `nano` instead of `echo ... > file`; use **Tab completion** to avoid typing underscores in filenames (`nano /etc/ssh/sshd` + Tab → `sshd_config`); `sed -i` also works when quoting is simple.
- Password typing is blind and error-prone; the Paste clipboard button is more reliable for passwords than for commands.
- The console keeps working when SSH is dead — it is the recovery path; don't close it until SSH is confirmed working.
- Keep console commands single and short; verify results with `ss -tln`, `systemctl status`, `journalctl -u ssh --no-pager -n 20` (no pipes needed).

## plink fails, native ssh works

`plink.exe` (PuTTY) dies with `FATAL ERROR: Network error: Software caused connection abort` on every attempt in this environment, even on paths where native `C:\Windows\System32\OpenSSH\ssh.exe` completes the handshake. **Use native OpenSSH; do not use plink.** Consequence: no `-pw` scripted password login — the one-time public-key install must be run interactively by the user (native ssh reads the password from the console, not stdin).

## Non-interactive key auth for automation

After the public key is in `~/.ssh/authorized_keys`, background shells work:

```powershell
ssh -p <port> -o BatchMode=yes root@<ip> "<command>"
```

`BatchMode=yes` fails fast instead of hanging on a password prompt — good for verifying key install.

## MTU blackhole: transfers that authenticate but hang on data

`git clone` (or any bulk transfer) that stalls right after "Cloning into ..." while `ssh -T git@github.com` authenticates fine = **PMTU blackhole**: small packets pass, large ones are dropped. One-line fix, then persist it:

```bash
sysctl -w net.ipv4.tcp_mtu_probing=1
printf 'net.ipv4.tcp_mtu_probing=1\n' > /etc/sysctl.d/99-mtu.conf
```

Try this BEFORE suspecting the remote service. Related workaround if outbound port 22 itself is filtered: GitHub over 443 — in `~/.ssh/config` under `Host github.com` add `HostName ssh.github.com` + `Port 443`.

## Private-repo deploy without workstation SSH

- Server generates its own keypair (`ssh-keygen -q -t ed25519 -N '' -f ~/.ssh/ghdep`); the PUBLIC key goes into GitHub repo Settings → Deploy keys (read-only). `~/.ssh/config`: `Host github.com` / `IdentityFile ...` / `StrictHostKeyChecking accept-new`. Verify: `ssh -T git@github.com` → "Hi <user>/<repo>!".
- Extracting the pubkey through a console screen without external paste services: `od -An -tx1 file` (hex is far less ambiguous than base64), transcribe, decode locally, verify against `md5sum` from the server; brute-force 1–2 hex-digit errors against the md5 if needed (i/l and 0/O misreads are common — one search found the exact key).
- systemd unit files build cleanly over a console as sequential `printf '...' >>` appends (each under ~100 chars), then `cat` to verify, `systemctl daemon-reload && systemctl enable --now <svc>`, and `curl -s localhost/<path>` as the smoke test.

## Russian VPS + Ubuntu mirrors

- `security.ubuntu.com` / `archive.ubuntu.com` are often unreachable or crawling from Russian VPS: `apt-get update` warns `Connection failed`, `apt upgrade` hangs for many minutes, and boot-time `apt-daily`/unattended-upgrades can wedge a 1 GB box (SSH unresponsive while console works).
- Fix first thing on a new box: switch APT to a Russian mirror in `/etc/apt/sources.list.d/ubuntu.sources` (e.g. `http://mirror.yandex.ru/ubuntu`), and disable/mask `apt-daily.timer` + `apt-daily-upgrade.timer` until the mirror is set.
- `journalctl` line `User sessions running outdated binaries: ... sshd` after an upgrade → restart `ssh` service at a convenient moment.

## Server identity check

`ssh -v ... 2>&1` prints `remote software version OpenSSH_<x> Ubuntu-<y>` — quick confirmation of the actual Ubuntu release before running version-dependent setup.

## Two managed servers: make each a fallback path to the other

When a deployment has two servers that can reach each other, wire the tooling to try the direct path first and fall back through the sibling automatically. This turns the single most common failure of this environment — the workstation's source IP getting SSH-filtered mid-path — from a work stoppage into a logged retry.

The failure looks like a dead server and is not one. `Test-NetConnection <ip> -Port <sshport>` returns `True`, but the client reports `kex_exchange_identification: read: Connection timed out` (or paramiko's `Error reading SSH protocol banner`). Confirm before blaming the host: reach it from the other server and check `uptime`, `systemctl is-active ssh`, the DROP counters of your own rate-limit rules, and `journalctl -u ssh`. If the journal shows the attempts arriving and dying at banner exchange while load is zero, the host is healthy and the path is filtered.

Two properties make the fallback possible, and both are design decisions worth taking deliberately at build time:

- Do NOT pin the second server's SSH to the first server's address, however tempting it looks when hardening. Pinning couples the two failures: lose the primary and you lose management of the secondary.
- Filtering is keyed to the source IP, so any different exit works. If the deployment is itself a VPN, connecting through it also clears the block.

Heavy automation accelerates the flagging — dozens of short-lived SSH sessions in an hour is enough. Reuse one connection for a batch of commands where possible instead of opening one per command.
