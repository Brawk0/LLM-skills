# FastAPI + Jinja2 web-CRUD patterns

Reusable patterns and traps from building an admin web app on top of the default database-development stack (FastAPI + Jinja2 + PostgreSQL + Caddy on a VPS). Load this reference when building or debugging a similar app.

## Templates

### TemplateResponse: use kwargs, not the legacy dict signature

Wrong (works with old Starlette, silently breaks on current versions):

```python
return templates.TemplateResponse("page.html", {"request": request, ...})
```

Fails with `TypeError: unhashable type: 'dict'` deep inside Jinja's template cache — the dict is being used as a cache key. Trap: the traceback points at Jinja internals, not your call site.

Correct:

```python
return templates.TemplateResponse(request=request, name="page.html", context={...})
```

### Register template globals for cross-page widgets

Anything called from `base.html` on every render (badge counts, permission checks, current user) belongs in `templates.env.globals`, not in every route's context dict. One place to add, zero routes to touch:

```python
templates.env.globals["current_user"] = lambda r: current_user(r)
templates.env.globals["pending_count"] = _pending_confirmations_count
```

Call in template as `{% set u = current_user(request) %}`.

## CSS/HTML

### `body > nav`, not `nav`, for a top-level sidebar

A bare `nav { position: fixed; ... }` in base.html **also** styles `<nav class="tabs">` used inside a page template — the tabs collapse into invisible fixed elements. Use the direct-descendant selector when the rule targets the top-level nav:

```css
body > nav { position: fixed; left: 0; top: 0; bottom: 0; ... }
body > nav a { ... }   /* not `nav a` */
```

Same applies to any HTML5 landmark element (`main`, `header`, `footer`) used both structurally and semantically inside content.

### Vertical form class: `.box.stack`

Default `<form class="box"><label>X <input></label>...</form>` renders as tight rows because inline-block labels flow left-to-right. For a top-to-bottom form (usual expectation for data-entry), keep the base class and add a modifier:

```css
form.box { background:#fff; border:1px solid #ddd; padding:.8rem; }
form.box label { display: inline-block; margin: .2rem .8rem .2rem 0; }
/* stacked variant */
form.box.stack label { display: block; margin: .5rem 0 .15rem; font-weight: 600; }
form.box.stack input:not([type=checkbox]):not([type=radio]),
form.box.stack textarea,
form.box.stack select { display:block; width:100%; max-width: 24rem; padding:.35rem; }
```

Toggling `stack` in the template alone flips the whole form vertical.

### Sidebar as an off-canvas drawer

Minimal admin-panel drawer without a framework. HTML in `base.html`:

```html
<button class="nav-toggle" id="navToggle">☰</button>
<div class="nav-backdrop" id="navBackdrop"></div>
<nav id="nav"> <div class="menu">…links…</div> </nav>
<script>
  const b = document.body, close = () => b.classList.remove('nav-open');
  navToggle.onclick = e => { e.stopPropagation(); b.classList.toggle('nav-open'); };
  navBackdrop.onclick = close;
  addEventListener('keydown', e => e.key === 'Escape' && close());
</script>
```

CSS: nav is `position:fixed; transform:translateX(-100%); transition:transform .18s;` by default; `body.nav-open > nav { transform: translateX(0) }` slides it in. Backdrop is `position:fixed; inset:0; opacity:0; pointer-events:none;` and gets `opacity:1; pointer-events:auto` when open. z-index: backdrop 15, nav 20, toggle 30 (button stays clickable when nav is open, closes-on-click on backdrop). Give `main` a `padding-top` at least the toggle button's height so it doesn't overlap first-row content.

### Print without a PDF library

Most «сохранить/распечатать отчёт» requirements are served by browser print + a `@media print` block that hides chrome:

```css
@media print {
  nav, .print-hide { display: none !important; }
  main { max-width: none; margin: 0; padding: 0; }
}
```

Trigger with `<button onclick="window.print()">Печать</button>`. User picks «Save as PDF» in the OS dialog. Works on desktop, Android, iOS.

## Auth middleware

### `PUBLIC_PATHS` + `PUBLIC_PREFIXES` (exact + startswith)

An auth gate that only checks exact paths breaks on `/static/*` and other tree-mounted resources. Keep two containers:

```python
PUBLIC_PATHS = {"/login", "/logout", "/api/login", "/sw.js", "/manifest.webmanifest"}
PUBLIC_PREFIXES = ("/static/",)

@app.middleware("http")
async def _auth_gate(request, call_next):
    path = request.url.path
    if path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES):
        return await call_next(request)
    ...
```

When you add a new public endpoint (PWA-related is the most common case), remember to add it to `PUBLIC_PATHS`, otherwise the gate returns 303 → `/login` before the route runs. Symptom: POST `/api/…` returns the HTML of the login page with 200.

### Route allowed ≠ links shown

If middleware lets a limited role reach a route in read-only mode, the template must **not** render action links that would send that role somewhere else the middleware blocks. Otherwise the UI 303s them on every click. Pass the role into the template and hide links:

```jinja
{% set is_teacher = u and u['role'] == 'teacher' %}
{% if is_teacher %}{{ l['grp'] }}{% else %}<a href="/groups/{{ l['group_id'] }}">{{ l['grp'] }}</a>{% endif %}
```

Middleware protects security, template protects UX. Both, always.

## Data model

### Role of access ≠ HR job title

Two orthogonal fields. `users.role ∈ {owner, admin, teacher}` drives what the app allows. `teachers.job_title` (нейропсихолог/логопед/тренер) is free-text on the person record, only used for reports and time sheets. Do not overload one field for both — the stakeholder will change one without wanting to change the other, and you'll break auth.

### Per-relationship pricing, not per-catalogue

For services where each client-service-professional triple has its own price/discount/margin (typical for tutoring, therapy, coaching, small clinics), put pricing on the `enrollments` (client, professional, service) row itself:

- `unit_price` — snapshot in `enrollment_tariffs(enrollment_id, duration_min, price)`.
- `discount_percent smallint` + `discount_reason text` on the enrollment.
- `center_share_percent smallint` on the enrollment — percent the business keeps; professional gets `100 - N`.

Payout SQL then joins `lessons → lesson_participants → enrollments` and computes `lp.price * (100 - COALESCE(e.center_share_percent, DEFAULT)) / 100`. `COALESCE` shields legacy rows from a later-added column.

Trap: don't try to define a single «formula for everyone». If the stakeholder says «под всех подогнать нельзя», the model must expose the per-enrollment knob directly, not fake averages.

### Time sheet as a query, not a table

An HR time sheet (rows: professionals, columns: days, cells: hours worked) is a pure aggregation over `lessons WHERE status='held'`. Recomputing on every render is fast enough well past thousands of lessons. Do not add a `time_sheet` table — you'll create a second source of truth that drifts from `lessons`.

## Notifications

### Three-layer plan for «remind me before event X»

1. **In-app widget + navbar badge** — SQL count of «past but not yet confirmed» rows, rendered on every page via a template global. First line of defense, works even if nothing else is wired.
2. **PWA + Web Push (VAPID + service worker)** — 3 files (`/manifest.webmanifest`, `/sw.js` served at root scope, icon PNGs). Works on desktop, Android; iOS 16.4+ needs the site added to Home Screen. Cover 95% of «нужно нативное приложение» requests without shipping an APK/IPA.
3. **Desktop companion** (PySide6 + PyInstaller `--onefile`) — only when the requirement is truly «окно поверх всех программ» on a specific admin PC, which browsers can't do. Reuses same login and same JSON API.

Prefer 1+2 first; add 3 only when the specific user's specific PC needs it. Skip SMS/messenger channels unless the venue-specific gateway is already free/available; they're per-message paid and add integrations without materially better UX than 2.

### `Service-Worker-Allowed: /` header

Serving `sw.js` from `/static/sw.js` scopes it to `/static/*` and it can't intercept push at the site root. Serve it from `/sw.js` (its own FastAPI route returning `FileResponse`) with `headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"}`.

### Action buttons in push

Payload includes an id needed to identify the event; `sw.js` shows `notification.actions` conditionally (only when payload has that id — test/generic pushes get plain notification). Handler POSTs to a `/api/…/quick-status` endpoint with `credentials: 'include'` — same session cookie as the browser tab. iOS silently ignores `actions` and falls back to click-through; design for that.

## PostgreSQL specifics

### `date + time` combines into `timestamp` in a query

For an event scheduled by `lesson_date DATE` and `start_time TIME`, filter «starts within N minutes» directly in SQL, don't compute in Python:

```sql
WHERE (lesson_date + start_time) BETWEEN %s AND %s   -- %s = timestamp
```

Cross-timezone gotcha: the sum is `timestamp` (without zone). If your app timezone matters, cast: `((lesson_date + start_time) AT TIME ZONE 'Europe/Moscow')`.

### `TRUNCATE … RESTART IDENTITY CASCADE` for a demo-data wipe

Cleanest way to reset a schema before handing it to the real customer: list the tables you want empty, `RESTART IDENTITY` resets serial sequences to 1, `CASCADE` handles foreign-key referents. Keep `users` and any settings table out of the list — the customer still needs to log in. Take a `pg_dump -Fc` first so the wipe is one `pg_restore` away.

### psycopg parameter binding: `IN` with a variable-length list

Writing `WHERE login NOT IN %s` and passing `(("nikita",),)` **does not** get you SQL like `NOT IN ('nikita')`. psycopg (both v2 and v3) sees a plain scalar substitution — the raw tuple is dropped into `$1` and PostgreSQL parses `NOT IN $1` as a syntax error at runtime, not at import:

```
psycopg.errors.SyntaxError: syntax error at or near "$1"
LINE 1: ... FROM users WHERE login NOT IN $1 ORDER BY ...
```

Two clean fixes:

- **`= ANY(%s)` / `<> ALL(%s)`** — pass a Python `list`, psycopg maps it to a PostgreSQL array. Works with 0, 1, or many elements without special-casing:

  ```python
  conn.execute("SELECT ... WHERE login <> ALL(%s)", (list(SHADOW_LOGINS),))
  # SHADOW_LOGINS may be a tuple; list() makes psycopg emit an array literal
  ```

- **`IN (SELECT unnest(%s::text[]))`** — same underlying trick, more explicit if the query is complex.

Do NOT do the string-formatting workaround (`"IN (" + ",".join(...) + ")"` with values sql-quoted by hand) — you leak SQL-injection through the first field that comes from user input. Always parametrise.

## Time: one timezone for the whole app

### Naive local timestamps + UTC server = a silent offset

Schedules are usually stored as **wall-clock** time split into `date` + `time`
columns (a lesson at 18:00 stays at 18:00 after a DST change — that is the
point). Those values carry no timezone. The server almost always runs UTC.
Comparing the two silently shifts everything by the UTC offset.

The trap is that PostgreSQL does not complain. `timestamp < timestamptz`
implicitly casts the naive side **to the session timezone**:

```sql
-- both wrong on a UTC server when the times are local wall clock
WHERE (lesson_date + start_time) < now()                       -- silent cast
WHERE (lesson_date + start_time) < now() AT TIME ZONE 'UTC'    -- explicitly UTC
```

Symptoms are indirect and easy to misdiagnose: a "check every N minutes" poller
looks like it only runs on page load, reminder pushes arrive hours late, a
badge counter stays at zero. The user reports the *symptom* ("the dialog only
appears when I log in"), and fixing the symptom adds a second timer that
changes nothing.

### Fix: compute "now" in the app, pass it as a parameter

Do not put `now()` inside the query — it resolves in the database's timezone.
One declared timezone, one helper, parameters everywhere:

```python
APP_TZ = ZoneInfo(os.environ.get("APP_TZ", "Europe/Moscow"))

def local_now() -> datetime:      # naive, same shape as what is in the DB
    return datetime.now(APP_TZ).replace(tzinfo=None)

def local_today() -> date:
    return local_now().date()
```

Then `... < %s` with `local_now()`. Behaviour no longer depends on the server's
`timedatectl` or the database's `TimeZone`.

Also replace `date.today()` with `local_today()`: on a UTC server, between
midnight and the UTC offset, "today" is still yesterday for the user.

Grep for all of these when auditing: `now()`, `AT TIME ZONE`, `utcnow()`,
`date.today()`. One user-visible complaint usually means several silent ones.

### Mobile polling: interval alone is not enough

Two independent reasons a browser poll stops working on a phone:

- **Suspended timers.** Mobile browsers throttle or freeze `setInterval` in a
  backgrounded tab. Pair every poll with a `visibilitychange` listener that
  re-checks when the tab becomes visible again.
- **Cached responses.** A polled `GET` is cacheable; a cached empty list means
  the dialog never appears. Set `Cache-Control: no-store` on the response *and*
  `fetch(url, {cache: 'no-store'})` on the client — a tell-tale user report is
  "it appeared after I cleared the cache".

```javascript
setInterval(check, 60000);
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') check();
});
```

## Tables that are read on a phone

Grouping rows under a per-group heading (`<h2>date</h2>` + its own table)
duplicates the header for every group and eats a phone screen. One table, one
header row, and the grouping value as the **first column printed only on the
first row of each group**, with a heavier border between groups. Reads better
and scrolls less.

When a filter pins a column to a single value (one teacher, one status), drop
that column: it repeats what the filter already says, and horizontal space is
the scarcest resource on a phone.

A filter that answers "why did this user open the page" should come
pre-applied: if a specialist opens a shared calendar to see their own schedule,
default the filter to them (via the `staff.user_id → users.id` link) and leave
an explicit way to clear it.

## Duplicate submissions and the way back

### Read the timestamps before reading the code

When a record appears twice, the server access log settles the cause faster
than any reasoning about the code. The gap between the two POSTs names it:

| Gap | Cause |
| --- | --- |
| sub-second | double click, or a client retry |
| a few seconds | the button was pressed again |
| tens of seconds | the form was filled in and submitted again |

Two separate POSTs each followed by its own GET is a human repeating the
action — not a framework bug, and not something a second timer or a
transaction will fix.

### An action whose result is not visible will be repeated

The usual root cause: after `POST → 303 → GET`, the page reloads **at the top**
while the new row lands in a table further down, unhighlighted. Nothing says
"it worked", so the operator does it again. Either show the result (scroll
anchor, highlighted new row, flash message) or defend against the repeat.

### Three layers, one per case

- **Client, fast repeat.** Block the second submit and disable the button.
  Two traps: disable **after** a tick (`setTimeout(..., 0)`) or the button's
  name/value never reaches the server; and skip forms whose inline
  `onsubmit="return confirm(...)"` was answered "no" — check
  `e.defaultPrevented` first.
- **Server, deliberate repeat.** Look for an existing record in the same slot
  and return a confirmation page listing what is already there. Prefer
  confirmation over a hard block when the "slot" is approximate — e.g. a
  back-dated form that does not ask for a time and defaults every record to
  the same hour will collide legitimately.
- **Server, already written.** See below.

### Every money-changing action needs an inverse in the UI

A guard like "a completed lesson may not be deleted, it has already affected
balances and payroll" is right, but "cannot be deleted" must not become
"cannot be corrected". If the only fix for an operator error is editing the
database by hand, the first mistake becomes a developer task.

Give the completed record an explicit reversal with a mandatory reason:
status goes to cancelled, the charges are zeroed, the reason and author are
stored and displayed. The row stays in the journal — the same append-only
discipline as corrections.

## Deployment

### One-command deploy script that reads env

`deploy/update.sh` on the server: `git pull`, `pip install -r requirements.txt`, run migrations. Migrations need env vars (DB URL). Load them at the top:

```bash
set -a; . /etc/tutor-center.env; set +a
```

Without this, migration scripts using `DATABASE_URL` fail with «password authentication failed» — env vars from systemd don't leak into a plain `bash deploy/update.sh` invocation.

### `.gitignore` for a PyInstaller-based companion app

If the same repo ships a desktop companion (`desktop/notifier.py` etc.), the 50 MB `.exe` and PyInstaller intermediates must not go into git:

```gitignore
desktop/build/
desktop/dist/
desktop/*.spec
desktop/.venv/
```

Ship a build recipe (`desktop/README.md`) instead; the maintainer rebuilds locally.

### Web Push: two silent-failure traps that cost hours

Both of these fail without a red exception — the UI just… waits. Skip them and you'll spend the debug session on the wrong file.

**Trap 1 — `pywebpush` cannot parse a PEM string.**
`webpush(vapid_private_key=<pem_string>)` internally calls `Vapid.from_string()`, which expects **raw base64**, not a PEM with `-----BEGIN/END-----`. You get `ValueError: Could not deserialize key data … ASN.1 parsing error: invalid length` on every send — the *keypair* is fine (`cryptography` and `Vapid.from_pem()` both load it), only the string entrypoint chokes.

Fix: write the PEM into a temp file at startup and pass the **file path**. `pywebpush` recognises paths and internally routes through `from_pem()`:

```python
_VAPID_TMP_PEM_PATH = None

def _vapid_pem_path() -> str | None:
    global _VAPID_TMP_PEM_PATH
    if _VAPID_TMP_PEM_PATH is not None:
        return _VAPID_TMP_PEM_PATH
    if not VAPID_PRIVATE_KEY_PEM:
        return None
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False, prefix="vapid-")
    f.write(VAPID_PRIVATE_KEY_PEM); f.close()
    try: os.chmod(f.name, 0o600)
    except Exception: pass
    _VAPID_TMP_PEM_PATH = f.name
    return _VAPID_TMP_PEM_PATH

# then:
webpush(subscription_info=..., data=..., vapid_private_key=_vapid_pem_path(),
        vapid_claims={"sub": VAPID_SUBJECT}, ttl=300)
```

**Trap 2 — `navigator.serviceWorker.ready` hangs forever on first visit.**
Standard UI pattern on a `/notifications` page: on load, `refresh()` reads the current subscription and shows either «Включить» or «Отключить». If the user has never registered the SW on this origin yet, `await navigator.serviceWorker.ready` **never resolves** — the status stays on «проверяю…», no button appears, user thinks the page is broken.

Use `getRegistration()` instead — it returns `undefined` immediately when nothing is registered:

```js
async function currentSubscription() {
  const reg = await navigator.serviceWorker.getRegistration();
  if (!reg) return null;
  return reg.pushManager.getSubscription();
}
```

**`.ready` is only safe AFTER you've called `.register()` at least once in this session.** For a status probe on page load — always `getRegistration()`.

### PySide6 tray-app: MUST have a single-instance lock

A tray-only Qt application has no visible window on startup. If the user runs the `.exe` twice, they get two silent tray icons — and Windows helpfully hides both of them in the collapsed overflow area (arrow `^` next to the clock). A non-technical user then thinks «it doesn't launch» while five copies are quietly holding RAM in the background, none configured, none doing anything.

Every PySide6 tray app MUST guard its `main()` with a lock:

```python
from PySide6.QtCore import QLockFile, QStandardPaths
from pathlib import Path

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

lock_dir = Path(QStandardPaths.writableLocation(QStandardPaths.TempLocation))
lockfile = QLockFile(str(lock_dir / "my-app.lock"))
lockfile.setStaleLockTime(0)  # crashed → previous lock is stale, take it
if not lockfile.tryLock(100):
    QMessageBox.information(None, "My App",
        "Приложение уже запущено — ищите иконку в трее "
        "(в Windows её часто прячет стрелочка ^ слева от часов).")
    return 0
# ... build tray, exec, then lockfile.unlock() in finally
```

Two rules that come with this:

- **Tell the user where to look.** The message MUST mention the collapsed-tray arrow explicitly — that's the whole failure mode. Don't just say «уже запущено».
- **`setStaleLockTime(0)`** — otherwise a hard-killed previous process leaves the lock forever and a legitimate restart also gets rejected.

If you skip the lock, the failure looks like «твой exe не запускается», you spend 40 minutes debugging why, then discover the user has 5 hidden copies. Been there.

### Destructive endpoints: guard by three walls, not one

Any endpoint that can wipe or overwrite user data (DB restore, mass delete, reset, drop-table migration) is worth building with **three independent barriers**, all server-side. Missing any one and the failure mode is «директор кликнул не туда → месяц данных пропал». Live example: `POST /settings/restore` in the tutoring-center project (commit `a2e43ae`).

**Wall 1 — role check.** `require(request, "owner")`. Never «admin can do it too, they know what they're doing» — you're saying that until the day admin doesn't.

**Wall 2 — phrase confirmation.** Not a checkbox «я согласен», not a red button labeled «точно уверен». Force the user to **type a specific word** into a text field:

```python
if (form.get("confirm") or "").strip() != "ВОССТАНОВИТЬ":
    return _render_result(ok=False, log="Не введено слово ВОССТАНОВИТЬ — защита от случайного клика.")
```

```html
<label>Подтверждение:
  <input name="confirm" placeholder="введите слово ВОССТАНОВИТЬ"
         autocomplete="off" required></label>
```

Reasoning: a checkbox can be ticked by mistake, a button with a scary label can be clicked while reading — but nobody types out «ВОССТАНОВИТЬ» accidentally.

**Wall 3 — safety snapshot BEFORE any change.** The very first side-effect of the endpoint MUST be a snapshot of the current state to a rollback file. If snapshot fails — abort, don't touch anything. If the destructive operation later returns weird results, the snapshot is your rollback in one command.

```python
stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
pre_path = AUTO_BACKUP_DIR / f"pre-restore-{stamp}.dump"
r = subprocess.run(["pg_dump", "-Fc", "-f", str(pre_path), db_url],
                   capture_output=True, text=True, timeout=120)
if r.returncode != 0:
    return _render_result(ok=False, log=f"Не удалось сделать страховочный бэкап — восстановление отменено:\n{r.stderr}")
# only NOW do the destructive thing
```

The filename prefix (`pre-restore-*`, `pre-migration-*`, `pre-wipe-*`) matters: makes rollback obvious 6 months later when nobody remembers what happened.

**Bonus — restart the process after DDL / schema-level operations.** The app's connection pool caches table metadata; if you `pg_restore --clean` under a running FastAPI, first queries through cached connections fail weirdly («relation does not exist», column-type mismatches). Fire the restart via `BackgroundTask` so the HTTP response reaches the user first:

```python
background_tasks.add_task(_restart_service)
return _render_result(ok=True, ...)

def _restart_service():
    subprocess.Popen(["systemctl", "restart", "my-app"])
```

A JS `onsubmit="return confirm(...)"` is fine as a nice-to-have — but it's an **extra** wall, not one of the three. JS can be bypassed, users can Enter-through without reading; the three server-side walls above must hold on their own.

## Pre-handoff QA (three independent passes)

Before letting a real user touch the app for the first time, run all three passes on an empty database (`TRUNCATE ... RESTART IDENTITY CASCADE`, keep only auth). Each pass catches a different class of bug; skipping any of them ships that class:

1. **GET sweep** — script logs in as owner, hits every listed URL (including edge cases: `/thing/999`, filters with no matches, months with no data, static files, PWA manifest and `/sw.js`). Fail any that: return ≥400 (except intended 404s); contain `Internal Server Error`, `Traceback`, or `UndefinedError` in the body. Fast (~30 s) and catches server crashes and Jinja variable typos but is blind to missing functionality.

2. **End-to-end creation flow with reconciliation** — POST-through the full business chain: subject → professional → client → per-relationship pricing → planned event → held event, then read every summary page (time sheet, salary, finance) and *check the numbers agree with each other to the kopeck*. Catches: no UI to create dictionary rows (very common — you built the client-facing pages but forgot the admin-side CRUD for reference data); one report updated when a new pricing component landed but sibling reports still using the old formula.

3. **Role check** — log in as the most restricted role, hit ~7 URLs with `-MaximumRedirection 0`. Assert the exact expected 200/303 for each. Middleware edits are easy to break silently for one role while everything looks fine for owner.

When a bug shows up in pass 2 or 3, fix it and rerun the pass — the bug you find is usually the entry point to a family of related ones.

After all three pass, wipe test data (`TRUNCATE ... RESTART IDENTITY CASCADE` + `DELETE FROM users WHERE login IN ('test%')`) before handing over.

### Every feature you ship, YOU verify — end to end, before saying it's done

Non-negotiable. «Страницы отдают 200» is not verification, it's a smoke test. Reporting a feature as working when you only checked that the template renders is how you hand the user a broken button and find out three days later.

For each new feature, before telling the user it's ready:

1. **Exercise the actual code path** the user will take — the POST endpoint, not just the GET that shows the form. If it's JS-driven, call the API the JS calls, with the same payload shape.
2. **Read back the resulting state from the database**, not from the HTTP response. `{"ok": true}` proves the handler didn't crash; `SELECT attendance, price, charge_source FROM ...` proves it did the right thing.
3. **Test the branches that matter.** A three-way attendance status needs all three checked: does `no_show` actually charge, does `excused` actually not, does `present` charge the discounted price. Testing only the happy path hides exactly the bugs that cost money.
4. **Check the numbers against hand-arithmetic.** 1800 ₽ with 17 % discount must land as 1494.00 — compute it yourself and compare, don't accept whatever the DB shows.
5. **If a result looks wrong, find out why before reporting.** In one case a `no_show` came back `price=0, free` — that turned out to be a test artefact (lesson created with a teacher who had no enrollment for that student), not a bug. Re-running with correct fixtures gave the right 1494.00. Reporting either «works» or «broken» without that second step would have been wrong.

Where to run it: never on prod after handover (see next section). Spin the scratch DB + second uvicorn on another port, run the full flow there, drop it after.

### After handover: NEVER run a data-creating E2E on the live database

Once the client has started entering real data, the pre-handoff QA loop is no longer available on prod. Re-running it there is worse than not testing:

- A `curl -X POST /students/... -d 'enrollment_id=1'` will land on **whatever enrollment id=1 exists in the client's data now**, not the one your test script imagined. Real symptom: my POST created a lesson under Uch2 (my test) using the teacher/subject taken from the client's Kozlov enrollment, mixing my test participant into the client's real professional's schedule. Ten seconds to write, thirty to clean up, an hour to realise something was off.
- Even shell mishaps compound: `GID=$(psql -tAc "SELECT id FROM groups WHERE name='TestGroup'")` returns an empty string when the group doesn't exist, then the next `curl .../groups/$GID/...` hits `.../groups//...` which some routes silently normalise to `/groups/` (list page) and others 404 — but the *creation* endpoint on the previous line already ran with whatever leaked through.

Rules for QA after handover:

- **Read-only diagnostics only against prod.** Sweep pass (GET) is fine — no rows changed. Role check is fine — no rows changed. E2E creation flow is **forbidden** against prod once the client is entering data.
- **For end-to-end verification, use one of:**
  1. **`pg_restore` last night's dump into a scratch database** (`CREATE DATABASE tutor_test OWNER ...` + `pg_restore -d tutor_test <dump>`), run a *second* uvicorn against that DB with `DATABASE_URL=postgresql://.../tutor_test`, hit it with your curl script, `DROP DATABASE tutor_test` when done. The prod service and prod DB are untouched.
  2. **Parallel dev deployment** — a second systemd unit (`tutor-center-dev.service`) on port 8001 that already exists in the project's dev setup, backed by its own `tutor_center_dev` DB. Same code, same schema, no real client data.
- **Always cross-check the DB before and after any prod write from a script:** `SELECT COUNT(*) FROM students, lessons, salary_adjustments` before → after; if anything changed that you didn't intend, roll it back **immediately** in a transaction before the client sees it. Real example: `DELETE FROM lesson_participants WHERE lesson_id=1; DELETE FROM lessons WHERE id=1; DELETE FROM enrollments WHERE id=2; DELETE FROM students WHERE id IN (3,4);` — restored the client's state in one transaction because I noticed within a minute.
- **API endpoints should enforce cross-field referential checks even if the UI already does.** `POST /students/{sid}/lessons` MUST verify `enrollment.student_id == sid`, not just `enrollment.id == enrollment_id`. A script with a wrong id in one field should get 404, not create hybrid data. Server can't assume the caller is a well-behaved browser form.
