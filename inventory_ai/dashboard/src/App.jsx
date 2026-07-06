import { Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Home from "./pages/Home.jsx";
import LiveDetection from "./pages/LiveDetection.jsx";
import Inventory from "./pages/Inventory.jsx";
import Verification from "./pages/Verification.jsx";
import Products from "./pages/Products.jsx";
import Workers from "./pages/Workers.jsx";
import History from "./pages/History.jsx";
import Analytics from "./pages/Analytics.jsx";
import Settings from "./pages/Settings.jsx";

export default function App() {
  return (
    <div className="flex min-h-screen bg-slate-950">
      <Sidebar />
      <main className="flex-1 p-6 overflow-x-hidden">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/live" element={<LiveDetection />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/verification" element={<Verification />} />
          <Route path="/products" element={<Products />} />
          <Route path="/workers" element={<Workers />} />
          <Route path="/history" element={<History />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}
