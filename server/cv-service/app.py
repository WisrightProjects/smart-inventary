import sys
import os
import cv2
import torch
from flask import Flask, jsonify
from flask_cors import CORS

# Add RT-DETRv2 to Python path so we can load the model
RT_DETR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'RT-DETRv2', 'rtdetrv2_pytorch'))
sys.path.append(RT_DETR_PATH)

app = Flask(__name__)
CORS(app)

# Global variables for model
model = None
device = 'cuda' if torch.cuda.is_available() else 'cpu'

def load_model():
    global model
    weights_path = os.path.join(RT_DETR_PATH, 'rtdetrv2_r18vd.pth')
    if os.path.exists(weights_path):
        try:
            # Simple loading attempt (in reality, depends on the RT-DETR src architecture)
            print(f"Loading RT-DETR model from {weights_path} onto {device}...")
            # For a proper load, you usually instantiate the model class then load_state_dict.
            # Here we simulate the loading process.
            # model = torch.load(weights_path, map_location=device)
            # model.eval()
            print("Model loaded successfully (simulation for now to avoid CPU lockups).")
            model = "loaded"
        except Exception as e:
            print(f"Error loading model: {e}")
    else:
        print(f"Weights file not found at {weights_path}")

# In a real scenario, you map bounding box coordinates to specific racks.
# For demonstration, we'll simulate random counts or hardcode a count for Room 2 / Rack D
RACK_ZONES = {
    'Room 1': ['A', 'B', 'C', 'D', 'E'],
    'Room 2': ['A', 'B', 'C', 'D', 'E'],
    'Room 3': ['A', 'B', 'C', 'D', 'E']
}

@app.route('/api/detect', methods=['GET'])
def detect():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    # Simulate grabbing a frame from camera
    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # cap.release()
    
    # Simulate inference results
    # results = model(frame)
    # ... logic to count objects in zones ...

    # We return a simulated "detected" count for Room 2 Rack D 
    # to trigger the mismatch in the Node backend!
    
    # The Node server expects an AI count. Let's say Room 2 Rack D has 12 items detected.
    detected_counts = []
    
    for room, racks in RACK_ZONES.items():
        for rack in racks:
            # We just return None for racks we didn't "scan" to let the backend use recordedQty
            # Or we return a specific simulated detection:
            if room == 'Room 2' and rack == 'D':
                detected_counts.append({
                    "room": room,
                    "rack": rack,
                    "count": 12 # Hardcoded "AI Detected" count
                })
            else:
                detected_counts.append({
                    "room": room,
                    "rack": rack,
                    "count": None # Means "no override, use DB"
                })

    return jsonify({"detections": detected_counts})

if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=5000, debug=True)
