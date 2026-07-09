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

router.get(
  '/',
  requireAdmin,
  asyncHandler(async (req, res) => {
    const days = Number(req.query.days || process.env.EXPIRY_ALERT_DAYS || 180);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const cutoff = new Date(today);
    cutoff.setDate(cutoff.getDate() + days);
    const cutoffStr = fmt(cutoff);
    const todayStr = fmt(today);

    const rows = await db
      .prepare(
        `SELECT product_id, name, room, rack, unit, qty, expiry_date FROM products
         WHERE expiry_date IS NOT NULL AND expiry_date <= ? ORDER BY expiry_date`
      )
      .all(cutoffStr);
    const products = rows.map((p) => ({ ...p, expired: p.expiry_date < todayStr }));

    res.json({ withinDays: days, alerts: products });
  })
);

module.exports = router;
