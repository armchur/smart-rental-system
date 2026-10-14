"""
Smart Rental System - Recognition Service (Flask)
Receives an equipment photo and returns the predicted class,
confidence and top-3 results. Preprocessing matches training (1/255).
"""
import os
import io
import json
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
import tensorflow as tf

# Find the model folder no matter where the service is started from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "smart_rental_vgg16.keras")
LABELS_PATH = os.path.join(BASE_DIR, "model", "class_labels.json")
CONFIDENCE_THRESHOLD = 0.65  # Chapter 3 specification

print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
with open(LABELS_PATH, "r") as f:
    class_labels = {int(k): v for k, v in json.load(f).items()}
print("Model ready. Classes:", list(class_labels.values()))

# Warmup inference so the first user scan is instant
print("Warming up model on dummy input...")
dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
_ = model.predict(dummy, verbose=0)
print("Model warmed up and ready!")


app = Flask(__name__)


def prepare_image(file_bytes):
    """Exactly the same steps as test_recognition.py"""
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize((224, 224))
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    try:
        img_array = prepare_image(request.files["image"].read())
    except Exception:
        return jsonify({"error": "Invalid image file"}), 400

    preds = model.predict(img_array, verbose=0)[0]
    best = int(np.argmax(preds))
    conf = float(preds[best])
    top3 = [
        {"class": class_labels[int(i)], "confidence": round(float(preds[i]) * 100, 2)}
        for i in np.argsort(preds)[::-1][:3]
    ]
    accepted = conf >= CONFIDENCE_THRESHOLD
    return jsonify({
        "prediction": class_labels[best],
        "confidence": round(conf * 100, 2),
        "accepted": accepted,
        "message": "Recognized" if accepted else "Low confidence - manual verification needed",
        "top3": top3,
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
