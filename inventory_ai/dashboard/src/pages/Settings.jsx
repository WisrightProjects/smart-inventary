export default function Settings() {
  return (
    <div className="flex flex-col gap-4 max-w-xl">
      <h2 className="text-xl font-semibold">Settings</h2>
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-sm space-y-3">
        <p className="text-slate-400">
          Camera source, RT-DETR checkpoint, confidence threshold, and other
          runtime settings are configured server-side in
          <code className="mx-1 px-1.5 py-0.5 bg-slate-800 rounded">inventory_ai/backend/config/settings.py</code>
          (or via environment variables prefixed <code className="px-1.5 py-0.5 bg-slate-800 rounded">INV_</code>).
        </p>
        <p className="text-slate-400">
          To switch from the laptop webcam to a USB or industrial camera, set
          <code className="mx-1 px-1.5 py-0.5 bg-slate-800 rounded">INV_CAMERA_SOURCE</code>
          to the new device index or stream URI and restart the backend — no
          frontend changes are required.
        </p>
      </div>
    </div>
  );
}
