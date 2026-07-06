import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function Inventory() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    api.get("/inventory").then(setItems).catch(() => {});
  }, []);

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold">Inventory</h2>
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-left">
            <tr>
              <th className="p-3">Name</th>
              <th>SKU</th>
              <th>Category</th>
              <th>Rack</th>
              <th>Box</th>
              <th>Stock</th>
              <th>Min</th>
              <th>Max</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {items.map((p) => (
              <tr key={p.id} className={p.current_stock <= p.minimum_stock ? "bg-rose-950/30" : ""}>
                <td className="p-3">{p.name}</td>
                <td>{p.sku}</td>
                <td>{p.category}</td>
                <td>{p.rack}</td>
                <td>{p.box_number}</td>
                <td>{p.current_stock}</td>
                <td>{p.minimum_stock}</td>
                <td>{p.maximum_stock}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
