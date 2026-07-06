import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Home" },
  { to: "/live", label: "Live Detection" },
  { to: "/inventory", label: "Inventory" },
  { to: "/verification", label: "Verification" },
  { to: "/products", label: "Products" },
  { to: "/workers", label: "Workers" },
  { to: "/history", label: "History" },
  { to: "/analytics", label: "Analytics" },
  { to: "/settings", label: "Settings" },
];

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 h-screen sticky top-0 bg-slate-900 border-r border-slate-800 p-4">
      <h1 className="text-lg font-semibold mb-6 text-slate-100">AI Inventory</h1>
      <nav className="flex flex-col gap-1">
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === "/"}
            className={({ isActive }) =>
              `px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-indigo-600 text-white"
                  : "text-slate-300 hover:bg-slate-800"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
