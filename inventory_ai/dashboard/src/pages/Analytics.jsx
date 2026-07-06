import { useEffect, useState } from "react";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";
import { api } from "../api/client.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Tooltip, Legend);

const chartOptions = {
  responsive: true,
  plugins: { legend: { labels: { color: "#cbd5e1" } } },
  scales: {
    x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
    y: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
  },
};

export default function Analytics() {
  const [daily, setDaily] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [statusBreakdown, setStatusBreakdown] = useState([]);
  const [stockMovement, setStockMovement] = useState([]);

  useEffect(() => {
    api.get("/analytics/daily-verifications").then(setDaily).catch(() => {});
    api.get("/analytics/top-products").then(setTopProducts).catch(() => {});
    api.get("/analytics/status-breakdown").then(setStatusBreakdown).catch(() => {});
    api.get("/analytics/stock-movement").then(setStockMovement).catch(() => {});
  }, []);

  const dailyData = {
    labels: daily.map((d) => d.date),
    datasets: [{ label: "Verifications", data: daily.map((d) => d.count), borderColor: "#6366f1", backgroundColor: "#6366f1" }],
  };

  const topProductsData = {
    labels: topProducts.map((p) => p.product),
    datasets: [{ label: "Frequency", data: topProducts.map((p) => p.count), backgroundColor: "#22c55e" }],
  };

  const statusData = {
    labels: statusBreakdown.map((s) => s.status),
    datasets: [{ label: "Count", data: statusBreakdown.map((s) => s.count), backgroundColor: "#f59e0b" }],
  };

  const stockData = {
    labels: stockMovement.map((s) => s.product),
    datasets: [{ label: "Current Stock", data: stockMovement.map((s) => s.current_stock), backgroundColor: "#f43f5e" }],
  };

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold">Analytics</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="font-medium mb-3 text-sm">Daily Verifications</h3>
          <Line data={dailyData} options={chartOptions} />
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="font-medium mb-3 text-sm">Top Products (Frequency)</h3>
          <Bar data={topProductsData} options={chartOptions} />
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="font-medium mb-3 text-sm">Verification Status Breakdown</h3>
          <Bar data={statusData} options={chartOptions} />
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="font-medium mb-3 text-sm">Lowest Stock Movement</h3>
          <Bar data={stockData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
}
