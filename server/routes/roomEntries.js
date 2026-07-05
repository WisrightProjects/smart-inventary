const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');

const router = express.Router();

function fmt(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function fmtTime(date) {
  const h = String(date.getHours()).padStart(2, '0');
  const m = String(date.getMinutes()).padStart(2, '0');
  return `${h}:${m}`;
}

function minutesBetween(a, b) {
  const [ah, am] = a.split(':').map(Number);
  const [bh, bm] = b.split(':').map(Number);
  return bh * 60 + bm - (ah * 60 + am);
}

// Admin: room-entry log for a given date.
router.get('/', requireAdmin, (req, res) => {
  const { date } = req.query;
  if (!date) return res.status(400).json({ error: 'date query param is required (YYYY-MM-DD)' });

  const rows = db
    .prepare(
      `SELECT date, entry_time, exit_time, employee_name, emp_id, rfid_tag, room, duration, status
       FROM room_entries WHERE date = ? ORDER BY entry_time`
    )
    .all(date);
  res.json(rows);
});

// Admin: who is currently inside a room right now (no exit scan yet).
router.get('/current', requireAdmin, (req, res) => {
  const rows = db
    .prepare(
      `SELECT date, entry_time, employee_name, emp_id, rfid_tag, room
       FROM room_entries WHERE exit_time IS NULL ORDER BY entry_time`
    )
    .all();
  res.json(rows);
});

// Admin/kiosk: scan an RFID tag at a room door. First scan of the day checks the
// employee in; if they already have an open entry, this scan checks them out.
router.post('/scan', requireAdmin, (req, res) => {
  const { rfidTag, room } = req.body || {};
  if (!rfidTag || !room) return res.status(400).json({ error: 'rfidTag and room are required' });

  const employee = db.prepare('SELECT * FROM employees WHERE rfid_tag = ?').get(rfidTag);
  if (!employee) return res.status(404).json({ error: `No employee is registered to tag "${rfidTag}"` });

  const now = new Date();
  const today = fmt(now);
  const time = fmtTime(now);

  const open = db
    .prepare('SELECT * FROM room_entries WHERE emp_id = ? AND exit_time IS NULL ORDER BY id DESC LIMIT 1')
    .get(employee.emp_id);

  if (open) {
    const duration = `${minutesBetween(open.entry_time, time)} mins`;
    db.prepare('UPDATE room_entries SET exit_time = ?, duration = ?, status = ? WHERE id = ?').run(
      time,
      duration,
      'Completed',
      open.id
    );
    return res.json({
      action: 'exit',
      employee: { name: employee.name, emp_id: employee.emp_id, department: employee.department },
      room: open.room,
      entry_time: open.entry_time,
      exit_time: time,
      duration,
    });
  }

  db.prepare(
    `INSERT INTO room_entries (date, emp_id, employee_name, rfid_tag, room, entry_time, exit_time, duration, status)
     VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, 'In Room')`
  ).run(today, employee.emp_id, employee.name, employee.rfid_tag, room, time);

  res.json({
    action: 'entry',
    employee: { name: employee.name, emp_id: employee.emp_id, department: employee.department },
    room,
    entry_time: time,
  });
});

module.exports = router;
