# User Stories
## Smart Inventory Management System (WisRight)

| Field | Value |
|---|---|
| Document Type | User Stories |
| Companion Doc | [PRD.md](PRD.md) |
| Status | Draft — for internal review |
| Last Updated | 2026-07-08 |

Stories are grouped by role, then by feature area. Each story follows
`As a <role>, I want <capability>, so that <benefit>` with acceptance
criteria that map to what's actually implemented in the codebase
(`server/`, `inventory_ai/`, `firmware/`).

---

## 1. System Administrator

### 1.1 Authentication & Access
**US-01** — As an Administrator, I want to log in with a username and password, so that only authorized staff can access stock, worker, and camera data.
- Acceptance: JWT-based login; invalid credentials rejected; session persists via token in local storage.

### 1.2 Live CCTV & Employee Monitoring
**US-02** — As an Administrator, I want to see a live video feed from the entrance IP camera and from each room's webcam, so that I can visually confirm who is on the floor without walking there.
- Acceptance: Monitoring → CCTV Monitoring page streams MJPEG video per zone (Entrance, Room 1); shows camera online/offline status.

**US-03** — As an Administrator, I want detected people automatically matched to their active RFID check-in session, so that I know *who* the camera is seeing, not just a person-shaped box.
- Acceptance: RT-DETR detection + ByteTrack tracking is cross-referenced against open `room_entries` sessions; matched people show name + entry time, unmatched show "Unknown Person".

**US-04** — As an Administrator, I want an alert when an unrecognized person is detected in a monitored room, so that I can respond to unauthorized access quickly.
- Acceptance: `unauthorized_person` alert posted after a configurable unmatched-detection duration (`MONITOR_UNKNOWN_ALERT_SECONDS`).

### 1.3 Inventory Oversight
**US-05** — As an Administrator, I want a dashboard of total stock, low-stock items, and today's movement count, so that I can spot problems at a glance.
- Acceptance: Home dashboard cards for total products, low-stock alerts, today's movements, active mismatches.

**US-06** — As an Administrator, I want to browse stock by Room → Rack, so that I know exactly where every product physically sits.
- Acceptance: Stock/Inventory page drills down Room 1–3 → Rack A–E → product list with quantity and expiry.

**US-07** — As an Administrator, I want to see a full RFID movement log for any date (past, today, or future), so that I can audit exactly who moved what and when.
- Acceptance: Date-picker view lists employee, room, rack, product, in/out time, and status (Completed / In Progress / No records for empty days).

**US-08** — As an Administrator, I want expiry alerts surfaced on the home screen, so that near-expiry stock gets used or removed before it's wasted.
- Acceptance: `/api/expiry-alerts` returns items within a configurable day window (`EXPIRY_ALERT_DAYS`), shown as a home-page notification list.

**US-09** — As an Administrator, I want to generate a QR code for any product, so that racks and boxes can be labeled for fast lookup.
- Acceptance: QR Generator page produces a scannable code encoding product ID/location.

### 1.4 Verification & Analytics
**US-10** — As an Administrator, I want AI-detected product counts checked against recorded quantities per rack, so that stock discrepancies are caught automatically instead of during a manual audit.
- Acceptance: Verification page shows MATCH / WRONG_PRODUCT / MISSING_PRODUCT / EXTRA_PRODUCT / UNEXPECTED_PRODUCT / MIXED_PRODUCTS per the verifier engine.

**US-11** — As an Administrator, I want charts of stock and movement trends over time, so that I can plan restocking instead of reacting to shortages.
- Acceptance: Analytics page aggregates historical transactions into trend/volume charts.

---

## 2. Warehouse Worker / Employee

### 2.1 Entry & Access
**US-12** — As a Worker, I want my RFID badge tap at the entrance to automatically log my check-in and check-out time, so that I don't need to fill out a manual attendance sheet.
- Acceptance: ESP32 EntranceUnit firmware — 1st tap logs in, 2nd tap on the same card logs out; `POST /api/rfid/checkin` / `checkout`.

**US-13** — As a Worker, I want to tap my badge at a rack to log which rack I accessed, so that my activity is recorded without extra manual entry.
- Acceptance: Rack Unit firmware reports "employee X accessed rack Y" for whichever badge is currently checked in.

### 2.2 Stock Lookup
**US-14** — As a Worker, I want to view current stock per room/rack without admin access, so that I can find what I need without asking a supervisor.
- Acceptance: Public Employee Stock view (no login) shows read-only room/rack/product overview.

**US-15** — As a Worker, I want to scan a product's QR code to instantly see its name, quantity, and correct rack location, so that I put items back in the right place.
- Acceptance: QR Scanner page (camera or manual code entry) resolves a product ID to its room/rack/quantity.

### 2.3 Movement Logging
**US-16** — As a Worker, I want my product pick/return actions logged with a timestamp automatically from my RFID scan, so that I don't have to manually write a stock ledger entry.
- Acceptance: Movement rows capture employee, room, rack, product, action (in/out), entry/exit time, and status.

---

## 3. Supervisor / Management

**US-17** — As a Supervisor, I want to see who is currently inside each room in real time, so that I can locate a worker without radioing around.
- Acceptance: "Currently Inside" live panel (Employee Monitoring tab) polls open `room_entries` sessions.

**US-18** — As a Supervisor, I want a per-date history of entries/exits and durations, so that I can review attendance patterns or investigate an incident after the fact.
- Acceptance: Entry/Exit History table filterable by date, showing entry, exit, duration, and status.

---

## 4. Cross-Cutting / Non-Functional Stories

**US-19** — As any user, I want the dashboard to clearly show camera offline/unreachable status rather than fail silently, so that I trust what "no alerts" actually means (verified quiet vs. broken monitoring).
- Acceptance: CCTV tab health-checks each monitor service and shows Online/Offline; API falls back gracefully rather than crashing when a camera/service is unreachable.

**US-20** — As a system owner, I want camera hardware to be swappable (webcam ↔ IP camera) via configuration only, so that a pilot on a laptop webcam can later move to real IP cameras without a code rewrite.
- Acceptance: `MONITOR_CAMERA_URL` env var switches source; documented in `docs/camera-swap.md`.

**US-21** — As a system owner, I want the product recognition model's real accuracy limits documented, so that stakeholders don't overestimate what's verified out-of-the-box vs. what needs fine-tuning.
- Acceptance: `inventory_ai/README.md` documents which COCO classes map to real catalog products today, and what requires custom training (`docs/training.md`).

---

## Traceability to PRD

| PRD Section | Covered By |
|---|---|
| §4.1 Labour Entry Tracking | US-12 |
| §4.2 Rack Identification | US-13, US-15 |
| §4.3 Manual Product Scan | US-16 |
| §4.4 AI + Tray Verification | US-10 |
| §4.5 Data Storage & Records | US-07, US-16 |
| §4.6 Employee Mobile Guide | US-14, US-15 |
| §4.7 Web Dashboard | US-05, US-06, US-08, US-11, US-17, US-18 |
| §4.8 Hardware / Connectivity | US-12, US-13, US-20 |
