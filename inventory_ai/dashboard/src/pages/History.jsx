import { useEffect, useState } from "react";
import { api } from "../api/client.js";

const STATUSES = [
  "",
  "VERIFIED",
  "WRONG_PRODUCT",
  "MISSING_PRODUCT",
  "EXTRA_PRODUCT",
  "UNEXPECTED_PRODUCT",
  "MIXED_PRODUCTS",
];

export default function History() {
  const [transactions, setTransactions] = useState([]);
  const [status, setStatus] = useState("");

  useEffect(() => {
    const query = status ? `?status=${status}&limit=200` : "?limit=200";
    api.get(`/history${query}`).then(setTransactions).catch(() => {});
  }, [status]);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Verification History</h2>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="bg-slate-800 rounded-md px-3 py-1.5 text-sm"
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s || "All Statuses"}</option>
          ))}
        </select>
      </div>
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-left">
            <tr>
              <th className="p-3">ID</th>
              <th>Worker</th>
              <th>Product</th>
              <th>Expected</th>
              <th>Detected</th>
              <th>Status</th>
              <th>Confidence</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {transactions.map((t) => (
              <tr key={t.id}>
                <td className="p-3">{t.id}</td>
                <td>{t.worker_id}</td>
                <td>{t.product_id}</td>
                <td>{t.expected_quantity}</td>
                <td>{t.detected_quantity}</td>
                <td>{t.verification_status}</td>
                <td>{t.confidence_score}</td>
                <td className="text-xs text-slate-500">{new Date(t.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
