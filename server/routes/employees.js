const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');
const { asyncHandler } = require('../middleware/asyncHandler');

const router = express.Router();

router.get(
  '/',
  requireAdmin,
  asyncHandler(async (req, res) => {
    const employees = await db.prepare('SELECT emp_id, name, rfid_tag, department, shift FROM employees ORDER BY emp_id').all();
    res.json(employees);
  })
);

module.exports = router;
