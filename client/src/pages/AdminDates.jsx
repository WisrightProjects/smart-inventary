import { useEffect, useState } from 'react';
import { api } from '../api.js';

function StatusBadge({ status }) {
  const cls = status === 'Completed' ? 'badge-completed' : 'badge-progress';
  return <span className={`badge ${cls}`}>{status}</span>;
}

export default function AdminDates() {
  const [dates, setDates] = useState([]);
  const [selected, setSelected] = useState(null);
  const [rows, setRows] = useState([]);
  const [roomEntryRows, setRoomEntryRows] = useState([]);

  useEffect(() => {
    api.getMovementDates().then((d) => {
      setDates(d);
      const today = d.find((x) => x.label === 'Today');
      if (today) selectDate(today.date);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function selectDate(date) {
    setSelected(date);
    api.getMovementsByDate(date).then(setRows).catch(() => setRows([]));
    api.getRoomEntries(date).then(setRoomEntryRows).catch(() => setRoomEntryRows([]));
  }

  return (
    <>
      <div className="card">
        <h2>Select a Date</h2>
        <div className="date-strip">
          {dates.map((d) => (
            <button
              key={d.date}
              className={`date-chip ${selected === d.date ? 'active' : ''}`}
              onClick={() => selectDate(d.date)}
            >
              {d.date}
              <span className="label">{d.label}</span>
            </button>
          ))}
        </div>
      </div>

      {selected && (
        <div className="card">
          <h2>Room Entry Log — {selected}</h2>
          {roomEntryRows.length === 0 ? (
            <p className="muted">No door scans recorded for this date.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>In Time</th>
                  <th>Employee</th>
                  <th>Emp ID</th>
                  <th>RFID Tag</th>
                  <th>Room</th>
                  <th>Out Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {roomEntryRows.map((r, i) => (
                  <tr key={i}>
                    <td>{r.entry_time}</td>
                    <td>{r.employee_name}</td>
                    <td>{r.emp_id}</td>
                    <td>{r.rfid_tag}</td>
                    <td>{r.room}</td>
                    <td>{r.exit_time || '--'}</td>
                    <td><StatusBadge status={r.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {selected && (
        <div className="card">
          <h2>RFID Movement Log — {selected}</h2>
          {rows.length === 0 ? (
            <p className="muted">No movement recorded for this date.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>In Time</th>
                  <th>Employee</th>
                  <th>Emp ID</th>
                  <th>Room</th>
                  <th>Rack</th>
                  <th>Action</th>
                  <th>Product</th>
                  <th>Out Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i}>
                    <td>{r.entry_time}</td>
                    <td>{r.employee_name}</td>
                    <td>{r.emp_id}</td>
                    <td>{r.room}</td>
                    <td>{r.rack}</td>
                    <td>{r.action}</td>
                    <td>{r.product_name}</td>
                    <td>{r.exit_time || '--'}</td>
                    <td><StatusBadge status={r.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </>
  );
}
