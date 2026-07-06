import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [category, setCategory] = useState("");

  useEffect(() => {
    const query = category ? `?category=${encodeURIComponent(category)}` : "";
    api.get(`/products${query}`).then(setProducts).catch(() => {});
  }, [category]);

  const categories = ["", "Stationery", "Books", "Office Supplies", "Electronics", "Accessories"];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Products</h2>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="bg-slate-800 rounded-md px-3 py-1.5 text-sm"
        >
          {categories.map((c) => (
            <option key={c} value={c}>{c || "All Categories"}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {products.map((p) => (
          <div key={p.id} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <p className="font-medium">{p.name}</p>
            <p className="text-xs text-slate-400">{p.sku} • {p.category}</p>
            <p className="text-xs text-slate-500 mt-2">Rack {p.rack} / Box {p.box_number}</p>
            <p className="text-sm mt-2">Stock: {p.current_stock}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
