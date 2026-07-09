const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');
const { asyncHandler } = require('../middleware/asyncHandler');

const router = express.Router();

const ROOMS = ['Room 1', 'Room 2', 'Room 3'];
const RACKS = ['A', 'B', 'C', 'D', 'E'];

router.get(
  '/overview',
  requireAdmin,
  asyncHandler(async (req, res) => {
    const cameras = [];

    // Fetch actual detections from Python microservice
    let aiDetections = {};
    let peopleCounts = {};
    try {
      const aiResponse = await fetch('http://127.0.0.1:5000/api/detect');
      if (aiResponse.ok) {
        const data = await aiResponse.json();
        data.detections.forEach((d) => {
          if (d.count !== null) {
            aiDetections[`${d.room}-${d.rack}`] = d.count;
          }
        });
        peopleCounts = data.people_counts || {};
      }
    } catch (err) {
      console.error("Could not reach Python CV service. Make sure it's running on port 5000.");
    }

    for (const room of ROOMS) {
      // YOLO Person Detection logic
      const personCount = peopleCounts[room] || 0;
      let identifiedEmployee = null;

      if (personCount > 0) {
        // Find the last person to scan into this room who hasn't exited (or just the most recent entry)
        const lastEntry = await db
          .prepare(`SELECT employee_name FROM room_entries WHERE room = ? ORDER BY date DESC, entry_time DESC LIMIT 1`)
          .get(room);

        if (lastEntry) {
          identifiedEmployee = lastEntry.employee_name;
        }
      }

      for (const rack of RACKS) {
        const { count: recordedCount, qty: recordedQty } = await db
          .prepare('SELECT COUNT(*) AS count, COALESCE(SUM(qty), 0) AS qty FROM products WHERE room = ? AND rack = ?')
          .get(room, rack);

        // Use AI count if available, otherwise fallback to recorded quantity
        const aiCount = aiDetections[`${room}-${rack}`] !== undefined ? aiDetections[`${room}-${rack}`] : Number(recordedQty);

        const lastActivity = await db
          .prepare(
            `SELECT date, entry_time, employee_name, action, product_name FROM movements
             WHERE room = ? AND rack = ? ORDER BY date DESC, entry_time DESC LIMIT 1`
          )
          .get(room, rack);

        cameras.push({
          room,
          rack,
          productTypes: Number(recordedCount),
          recordedQty: Number(recordedQty),
          aiCount,
          status: aiCount === Number(recordedQty) ? 'match' : 'mismatch',
          lastActivity: lastActivity || null,
          personDetected: personCount > 0,
          identifiedEmployee,
        });
      }
    }

    res.json({ simulated: false, cameras });
  })
);

module.exports = router;
