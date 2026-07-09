require('dotenv').config();
const express = require('express');
const cors = require('cors');

const db = require('./db');

const authRoutes = require('./routes/auth');
const employeeRoutes = require('./routes/employees');
const productRoutes = require('./routes/products');
const movementRoutes = require('./routes/movements');
const expiryRoutes = require('./routes/expiry');
const roomEntryRoutes = require('./routes/roomEntries');
const cctvRoutes = require('./routes/cctv');
const rfidRoutes = require('./routes/rfid');
const alertRoutes = require('./routes/alerts');
const monitorRoutes = require('./routes/monitor');
const transferRoutes = require('./routes/transfers');

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api/auth', authRoutes);
app.use('/api/employees', employeeRoutes);
app.use('/api/products', productRoutes);
app.use('/api/movements', movementRoutes);
app.use('/api/expiry-alerts', expiryRoutes);
app.use('/api/room-entries', roomEntryRoutes);
app.use('/api/cctv', cctvRoutes);
app.use('/api/rfid', rfidRoutes);
app.use('/api/alerts', alertRoutes);
app.use('/api/monitor', monitorRoutes);
app.use('/api/transfers', transferRoutes);

app.get('/api/health', (req, res) => res.json({ ok: true }));

// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

const PORT = process.env.PORT || 4000;

db.init()
  .then(() => {
    app.listen(PORT, () => console.log(`Smart Inventory API listening on port ${PORT}`));
  })
  .catch((err) => {
    console.error('Failed to initialize database:', err);
    process.exit(1);
  });
