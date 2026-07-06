# Replacing the Laptop Webcam with a USB or Industrial Camera

The system was designed so the camera source is a single configuration
value, not something wired into the detection/verification logic. This is
why `backend/camera/webcam_stream.py` takes `settings.camera_source` and
never hardcodes a device.

## Steps

1. **Identify the new camera's OpenCV source identifier**:
   - USB camera: usually an integer index (`0`, `1`, `2`, ...). Unplug/replug
     and check `cv2.VideoCapture(n).isOpened()` for each `n` to find it.
   - Industrial camera with a GigE/RTSP interface: use its stream URI, e.g.
     `rtsp://192.168.1.50:554/stream1`.

2. **Set the new source** via environment variable (no code changes):

   ```bash
   set INV_CAMERA_SOURCE=1
   ```

   or for a network camera:

   ```bash
   set INV_CAMERA_SOURCE=rtsp://192.168.1.50:554/stream1
   ```

3. **Adjust resolution if needed** — industrial cameras often support higher
   resolutions than a laptop webcam:

   ```bash
   set INV_CAMERA_WIDTH=1920
   set INV_CAMERA_HEIGHT=1080
   ```

4. **Restart the backend**. `WebcamStream` reconnects automatically if the
   camera drops, so no other changes are required — the live detection
   page, verification endpoint, and MJPEG stream all keep working
   unmodified.

## Mounting Notes for the Verification Tray

- Mount the camera directly above the transparent tray, perpendicular to
  its base, to minimize perspective distortion.
- Use controlled, diffuse lighting (avoid glare off the transparent tray
  material) and a plain white background — this matches the assumptions
  the RT-DETR fine-tuning dataset should be collected under (see
  [training.md](training.md)).
- If you retrain the model with images captured by the new camera's exact
  mounting position and lighting, detection accuracy will be notably higher
  than reusing a model trained on webcam images.
