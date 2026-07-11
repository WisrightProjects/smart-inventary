import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Video,
  Boxes,
  ScanLine,
  Package,
  Users,
  History as HistoryIcon,
  BarChart3,
  Settings as SettingsIcon,
  QrCode,
  ChevronsLeft,
  ChevronsRight,
  LogOut,
} from "lucide-react";
import Logo from "./Logo.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const LINKS = [
  { to: "/", label: "Home", icon: LayoutDashboard },
  { to: "/live", label: "Live Detection", icon: Video },
  { to: "/inventory", label: "Inventory", icon: Boxes },
  { to: "/verification", label: "Verification", icon: ScanLine },
  { to: "/products", label: "Products", icon: Package },
  { to: "/workers", label: "Workers", icon: Users },
  { to: "/analytics", label: "Analytics", icon: BarChart3, adminOnly: true },
  { to: "/qr-generator", label: "QR Generator", icon: QrCode, adminOnly: true },
  { to: "/qr-scanner", label: "QR Scanner", icon: ScanLine },
  { to: "/settings", label: "Settings", icon: SettingsIcon, adminOnly: true },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const links = LINKS.filter((link) => !link.adminOnly || user?.role === "admin");

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const displayName = user?.name || user?.empId || "User";
  const displayRole = user?.role === "admin" ? "Administrator" : user?.role === "employee" ? "Employee" : "";

  return (
    <aside
      className={`${
        collapsed ? "w-20" : "w-64"
      } shrink-0 h-screen sticky top-0 bg-slate-900 border-r border-slate-800 flex flex-col transition-all duration-300 z-20`}
    >
      <div className="h-16 flex items-center px-4 border-b border-slate-800">
        <Logo collapsed={collapsed} dark />
      </div>

      <nav className="flex-1 flex flex-col gap-0.5 px-3 py-4 overflow-y-auto">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              title={collapsed ? link.label : undefined}
              className={({ isActive }) =>
                `group flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-150 ${
                  isActive
                    ? "bg-slate-800 text-white"
                    : "text-slate-400 hover:bg-slate-800/70 hover:text-slate-200"
                }`
              }
            >
              <Icon size={17} strokeWidth={2.1} className="shrink-0" />
              {!collapsed && <span className="truncate">{link.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      <button
        onClick={() => setCollapsed((c) => !c)}
        className="mx-3 mb-3 flex items-center justify-center gap-2 py-2 rounded-lg text-slate-500 hover:bg-slate-800/70 hover:text-slate-200 transition-colors text-xs font-medium"
      >
        {collapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
        {!collapsed && "Collapse"}
      </button>

      <div className="border-t border-slate-800 p-3.5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-white font-semibold text-sm shrink-0">
            {displayName.charAt(0).toUpperCase()}
          </div>
          {!collapsed && (
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-white truncate">{displayName}</p>
              <p className="text-xs text-slate-400 truncate">{displayRole}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            title="Log out"
            className="w-8 h-8 shrink-0 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-800 hover:text-danger transition-colors"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
