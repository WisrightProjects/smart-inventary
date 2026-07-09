const express = require('express');
const db = require('../db');
const { asyncHandler } = require('../middleware/asyncHandler');

const router = express.Router();

const ROOMS = ['Room 1', 'Room 2', 'Room 3'];
const RACKS = ['A', 'B', 'C', 'D', 'E'];

// Public: overview of rooms with rack + product counts (used by both admin & employee stock pages).
router.get(
  '/overview',
  asyncHandler(async (req, res) => {
    const overview = [];
    for (const room of ROOMS) {
      const racks = [];
      for (const rack of RACKS) {
        const { count, qty } = await db
          .prepare('SELECT COUNT(*) AS count, COALESCE(SUM(qty), 0) AS qty FROM products WHERE room = ? AND rack = ?')
          .get(room, rack);
        racks.push({ rack, productCount: Number(count), totalQty: Number(qty) });
      }
      overview.push({ room, racks });
    }
    res.json(overview);
  })
);

// Public: full catalog, optionally filtered by room and/or rack. With no query
// params, returns every product (used by the Products page's catalog grid).
router.get(
  '/',
  asyncHandler(async (req, res) => {
    const { room, rack } = req.query;

    if (room && rack) {
      const products = await db
        .prepare('SELECT product_id, name, room, rack, unit, qty, expiry_date FROM products WHERE room = ? AND rack = ? ORDER BY product_id')
        .all(room, rack);
      return res.json(products);
    }

    if (room) {
      const products = await db
        .prepare('SELECT product_id, name, room, rack, unit, qty, expiry_date FROM products WHERE room = ? ORDER BY rack, product_id')
        .all(room);
      return res.json(products);
    }

    const products = await db
      .prepare('SELECT product_id, name, room, rack, unit, qty, expiry_date FROM products ORDER BY room, rack, product_id')
      .all();
    res.json(products);
  })
);

// Public: single product by product_id
router.get(
  '/:productId',
  asyncHandler(async (req, res) => {
    const { productId } = req.params;
    const product = await db
      .prepare('SELECT product_id, name, room, rack, unit, qty, expiry_date FROM products WHERE product_id = ?')
      .get(productId);

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    res.json(product);
  })
);

module.exports = router;
