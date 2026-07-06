import { useEffect, useState } from "react";
import Card from "../components/Card.jsx";
import { api } from "../api/client.js";

export default function Home() {
  const [accuracy, setAccuracy] = useState(null);
  const [mismatch, setMismatch] = useState(null);
  const [lowStock, setLowStock] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [recent, setRecent] = useState([]);
  const [cameraStatus, setCameraStatus] = useState(null);

  useEffect(() => {
    api.get("/analytics/accuracy").then(setAccuracy).catch(() => {});
    api.get("/analytics/mismatch-percentage").then(setMismatch).catch(() => {});
    api.get("/inventory/low-stock").then(setLowStock).catch(() => {});
    api.get("/alerts?resolved=false&limit=10").then(setAlerts).catch(() => {});
    api.get("/history?limit=10").then(setRecent).catch(() => {});
    api.get("/live/status").then(setCameraStatus).catch(() => {});
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold">Overview</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card title="Total Verifications" value={accuracy?.total ?? "-"} />
        <Card
          title="Verified"
          value={accuracy?.verified ?? "-"}
          accent="text-emerald-400"
          sub={accuracy ? `${accuracy.accuracy_percent}% accuracy` : ""}
        />
        <Card
          title="Mismatches"
          value={mismatch?.mismatches ?? "-"}
          accent="text-amber-400"
          sub={mismatch ? `${mismatch.mismatch_percent}%` : ""}
        />
        <Card
          title="Camera"
          value={cameraStatus?.connected ? "Online" : "Offline"}
          accent={cameraStatus?.connected ? "text-emerald-400" : "text-rose-400"}
          sub={cameraStatus ? `${cameraStatus.fps} FPS` : ""}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="font-medium mb-3">Low Stock ({lowStock.length})</h3>
          <ul className="text-sm divide-y divide-slate-800">
            {lowStock.slice(0, 8).map((p) => (
              <li key={p.id} className="py-2 flex justify-between">
                <span>{p.name} (Box {p.box_number})</span>
                <span className="text-amber-400">{p.current_stock} / {p.minimum_stock}</span>
              </li>
            ))}
            {lowStock.length === 0 && <li className="py-2 text-slate-500">No low stock items.</li>}
          </ul>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="font-medium mb-3">Active Alerts ({alerts.length})</h3>
          <ul className="text-sm divide-y divide-slate-800">
            {alerts.map((a) => (
              <li key={a.id} className="py-2 flex flex-col">
                <span className={a.severity === "critical" ? "text-rose-400" : "text-amber-400"}>
                  {a.message}
                </span>
              </li>
            ))}
            {alerts.length === 0 && <li className="py-2 text-slate-500">No active alerts.</li>}
          </ul>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
        <h3 className="font-medium mb-3">Recent Transactions</h3>
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-left">
            <tr>
              <th className="py-1">ID</th>
              <th>Product</th>
              <th>Expected</th>
              <th>Detected</th>
              <th>Status</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {recent.map((t) => (
              <tr key={t.id}>
                <td className="py-1">{t.id}</td>
                <td>{t.product_id}</td>
                <td>{t.expected_quantity}</td>
                <td>{t.detected_quantity}</td>
                <td>{t.verification_status}</td>
                <td>{t.confidence_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
