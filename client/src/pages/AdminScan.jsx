import { useEffect, useRef, useState } from 'react';
import { api } from '../api.js';

const ROOMS = ['Room 1', 'Room 2', 'Room 3'];

export default function AdminScan() {
  const [room, setRoom] = useState('Room 1');
  const [tag, setTag] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!tag.trim() || busy) return;
    setBusy(true);
    setError('');
    try {
      const data = await api.scanRfid(tag.trim(), room);
      setResult(data);
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setTag('');
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  return (
    <>
      <div className="card">
        <h2>RFID Door Scan</h2>
        <p className="muted">
          Point a USB/handheld RFID reader at this field (it types the tag like a keyboard), or type a tag ID
          manually and press Enter. Scanning a tag checks the employee in; scanning the same tag again checks
          them out.
        </p>

        <div className="grid-buttons" style={{ gridTemplateColumns: 'repeat(3, minmax(120px, 1fr))', marginBottom: 18 }}>
          {ROOMS.map((r) => (
            <button
              key={r}
              className={`rack-tag ${room === r ? 'active' : ''}`}
              onClick={() => setRoom(r)}
              type="button"
            >
              <span className="rack-letter">{r.replace('Room ', '')}</span>
              <span className="rack-caption">{r}</span>
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 10 }}>
          <input
            ref={inputRef}
            className="scan-input"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="Scan or type RFID tag (e.g. RFID1001)"
            autoComplete="off"
          />
          <button className="submit-btn" style={{ width: 'auto', padding: '10px 22px' }} disabled={busy}>
            Scan
          </button>
        </form>
        {error && <div className="error-text" style={{ marginTop: 14 }}>{error}</div>}
      </div>

      {result && (
        <div className={`card scan-result ${result.action === 'entry' ? 'scan-in' : 'scan-out'}`}>
          <h2>{result.action === 'entry' ? 'Checked In' : 'Checked Out'}</h2>
          <div className="scan-result-name">{result.employee.name}</div>
          <div className="muted">
            {result.employee.emp_id} &middot; {result.employee.department}
          </div>
          {result.action === 'entry' ? (
            <p style={{ marginTop: 12 }}>
              Entered <strong>{result.room}</strong> at <strong>{result.entry_time}</strong>
            </p>
          ) : (
            <p style={{ marginTop: 12 }}>
              Left <strong>{result.room}</strong> at <strong>{result.exit_time}</strong> (in: {result.entry_time},
              duration {result.duration})
            </p>
          )}
        </div>
      )}
    </>
  );
}
