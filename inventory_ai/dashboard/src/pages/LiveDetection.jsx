import { useEffect, useRef, useState } from "react";
import { api } from "../api/client.js";

export default function LiveDetection() {
  const [status, setStatus] = useState(null);
  const [detections, setDetections] = useState([]);
  const [counts, setCounts] = useState({});
  const pollRef = useRef(null);

  const refresh = () => {
    api.get("/live/detections").then((data) => {
      setStatus(data.camera);
      setDetections(data.detections);
      setCounts(data.counts);
    }).catch(() => {});
  };

  useEffect(() => {
    api.get("/live/status").then(setStatus).catch(() => {});
    pollRef.current = setInterval(refresh, 1500);
    return () => clearInterval(pollRef.current);
  }, []);

  const start = () => api.post("/live/start", {}).then(setStatus);
  const stop = () => api.post("/live/stop", {}).then(setStatus);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Live Detection</h2>
        <div className="flex gap-2">
          <button onClick={start} className="px-3 py-1.5 bg-emerald-600 rounded-md text-sm">Start Webcam</button>
          <button onClick={stop} className="px-3 py-1.5 bg-rose-600 rounded-md text-sm">Stop Webcam</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <img src="/api/live/stream" alt="live camera feed" className="w-full h-auto bg-black" />
        </div>

        <div className="flex flex-col gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-sm">
            <p>Status: <span className={status?.connected ? "text-emerald-400" : "text-rose-400"}>
              {status?.connected ? "Connected" : "Disconnected"}
            </span></p>
            <p>FPS: {status?.fps ?? 0}</p>
            <p>Source: {status?.source}</p>
            {status?.last_error && <p className="text-rose-400">Error: {status.last_error}</p>}
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <h3 className="font-medium mb-2 text-sm">Detected Counts</h3>
            <ul className="text-sm divide-y divide-slate-800">
              {Object.entries(counts).map(([name, count]) => (
                <li key={name} className="py-1 flex justify-between">
                  <span>{name}</span>
                  <span>{count}</span>
                </li>
              ))}
              {Object.keys(counts).length === 0 && (
                <li className="py-1 text-slate-500">No detections yet.</li>
              )}
            </ul>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <h3 className="font-medium mb-2 text-sm">Raw Detections</h3>
            <ul className="text-xs divide-y divide-slate-800 max-h-64 overflow-y-auto">
              {detections.map((d, i) => (
                <li key={i} className="py-1">
                  {d.name} — {(d.confidence * 100).toFixed(1)}%
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
