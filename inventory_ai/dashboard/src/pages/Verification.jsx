import { useEffect, useState } from "react";
import { api } from "../api/client.js";

const STATUS_COLORS = {
  VERIFIED: "text-emerald-400",
  WRONG_PRODUCT: "text-rose-400",
  MISSING_PRODUCT: "text-amber-400",
  EXTRA_PRODUCT: "text-amber-400",
  UNEXPECTED_PRODUCT: "text-orange-400",
  MIXED_PRODUCTS: "text-rose-400",
};

export default function Verification() {
  const [boxId, setBoxId] = useState("");
  const [workerId, setWorkerId] = useState("");
  const [workers, setWorkers] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/workers").then(setWorkers).catch(() => {});
  }, []);

  const runVerification = async () => {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await api.post("/verify", { box_id: boxId, worker_id: Number(workerId) });
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <h2 className="text-xl font-semibold">Box Verification</h2>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col gap-3">
        <label className="text-sm">
          Box ID
          <input
            value={boxId}
            onChange={(e) => setBoxId(e.target.value)}
            placeholder="e.g. B001"
            className="mt-1 w-full bg-slate-800 rounded-md px-3 py-2 text-sm"
          />
        </label>
        <label className="text-sm">
          Worker
          <select
            value={workerId}
            onChange={(e) => setWorkerId(e.target.value)}
            className="mt-1 w-full bg-slate-800 rounded-md px-3 py-2 text-sm"
          >
            <option value="">Select worker</option>
            {workers.map((w) => (
              <option key={w.id} value={w.id}>{w.name} — {w.department}</option>
            ))}
          </select>
        </label>
        <button
          onClick={runVerification}
          disabled={!boxId || !workerId || loading}
          className="bg-indigo-600 disabled:opacity-40 rounded-md py-2 text-sm"
        >
          {loading ? "Verifying..." : "Scan & Verify"}
        </button>
      </div>

      {error && <p className="text-rose-400 text-sm">{error}</p>}

      {result && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className={`text-lg font-semibold ${STATUS_COLORS[result.status] || ""}`}>
            {result.status.replace("_", " ")}
          </h3>
          <p className="text-sm text-slate-400 mt-1">{result.details}</p>
          <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
            <div>
              <h4 className="text-slate-400 mb-1">Expected</h4>
              <pre className="bg-slate-800 rounded-md p-2">{JSON.stringify(result.expected, null, 2)}</pre>
            </div>
            <div>
              <h4 className="text-slate-400 mb-1">Detected</h4>
              <pre className="bg-slate-800 rounded-md p-2">{JSON.stringify(result.detected, null, 2)}</pre>
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-3">Confidence: {result.confidence} • Transaction #{result.transaction_id}</p>
        </div>
      )}
    </div>
  );
}
