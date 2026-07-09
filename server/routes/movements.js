const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');
const { asyncHandler } = require('../middleware/asyncHandler');

const router = express.Router();

function fmt(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

// Admin: list of selectable dates - past 5, today, future 5 (relative to server clock).
router.get('/dates', requireAdmin, (req, res) => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const dates = [];
  for (let offset = -5; offset <= 5; offset++) {
    const d = new Date(today);
    d.setDate(d.getDate() + offset);
    dates.push({ date: fmt(d), label: offset === 0 ? 'Today' : offset < 0 ? `${-offset} day(s) ago` : `In ${offset} day(s)` });
  }
  res.json(dates);
});

// Admin: full movement table for a given date (time, employee, room, rack, product, action, in/out, status).
router.get(
  '/',
  requireAdmin,
  asyncHandler(async (req, res) => {
    const { date } = req.query;
    if (!date) return res.status(400).json({ error: 'date query param is required (YYYY-MM-DD)' });

    const rows = await db
      .prepare(
        `SELECT date, entry_time, exit_time, employee_name, emp_id, room, rack, product_id, product_name, action, duration, status, quantity, source, notes
         FROM movements WHERE date = ? ORDER BY entry_time`
      )
      .all(date);
    res.json(rows);
  })
);

// Admin: in/out counts for a room+rack on a given date, defaulting to yesterday/today/tomorrow.
router.get(
  '/summary',
  requireAdmin,
  asyncHandler(async (req, res) => {
    const { room, rack, date } = req.query;
    if (!room || !rack) return res.status(400).json({ error: 'room and rack query params are required' });

    if (date) {
      const rows = await db
        .prepare(
          `SELECT product_id, product_name, action, entry_time, exit_time, employee_name, status
           FROM movements WHERE room = ? AND rack = ? AND date = ? ORDER BY entry_time`
        )
        .all(room, rack, date);
      return res.json({ [date]: rows });
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const result = {};
    for (const offset of [-1, 0, 1]) {
      const d = new Date(today);
      d.setDate(d.getDate() + offset);
      const key = fmt(d);
      result[key] = await db
        .prepare(
          `SELECT product_id, product_name, action, entry_time, exit_time, employee_name, status
           FROM movements WHERE room = ? AND rack = ? AND date = ? ORDER BY entry_time`
        )
        .all(room, rack, key);
    }
    res.json(result);
  })
);

function nowTime(date) {
  return date.toTimeString().slice(0, 8);
}

// Admin: manually log a stock placement (e.g. new stock arriving and being
// sent to a room/rack) without going through the RFID/vision pipeline.
router.post(
  '/',
  requireAdmin,
  asyncHandler(async (req, res) => {
    const { empId, productId, room, rack, action, quantity, notes } = req.body;
    if (!empId || !productId || !room || !rack) {
      return res.status(400).json({ error: 'empId, productId, room, and rack are required' });
    }

    const employee = await db.prepare('SELECT name FROM employees WHERE emp_id = ?').get(empId);
    if (!employee) return res.status(404).json({ error: 'Employee not found' });

    const product = await db.prepare('SELECT name FROM products WHERE product_id = ?').get(productId);
    if (!product) return res.status(404).json({ error: 'Product not found' });

    const now = new Date();
    const { rows } = await db
      .prepare(
        `INSERT INTO movements
           (date, emp_id, employee_name, room, rack, product_id, product_name, action, entry_time, status, quantity, source, notes)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
         RETURNING id`
      )
      .run(
        fmt(now),
        empId,
        employee.name,
        room,
        rack,
        productId,
        product.name,
        action || 'Stock In',
        nowTime(now),
        'Completed',
        quantity != null ? Number(quantity) : null,
        'manual',
        notes || null
      );

    res.status(201).json({ id: rows[0].id });
  })
);

module.exports = router;
