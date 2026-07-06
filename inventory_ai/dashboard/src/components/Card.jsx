export default function Card({ title, value, accent = "text-slate-100", sub }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wide text-slate-400">{title}</span>
      <span className={`text-2xl font-semibold ${accent}`}>{value}</span>
      {sub && <span className="text-xs text-slate-500">{sub}</span>}
    </div>
  );
}
