import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function Workers() {
  const [workers, setWorkers] = useState([]);

  useEffect(() => {
    api.get("/workers").then(setWorkers).catch(() => {});
  }, []);

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold">Workers</h2>
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-left">
            <tr>
              <th className="p-3">ID</th>
              <th>Name</th>
              <th>Department</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {workers.map((w) => (
              <tr key={w.id}>
                <td className="p-3">{w.id}</td>
                <td>{w.name}</td>
                <td>{w.department}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
