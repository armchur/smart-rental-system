"""
Smart Rental System - Recognition Test Script
Tests model loading and inference with confidence score checking.
"""
import os
import json
import numpy as np
from PIL import Image
import tensorflow as tf

MODEL_PATH = os.path.join("model", "smart_rental_vgg16.keras")
LABELS_PATH = os.path.join("model", "class_labels.json")

CONFIDENCE_THRESHOLD = 0.65  # 65% per Chapter 3 specification

print("Loading trained VGG16 model...")
model = tf.keras.models.load_model(MODEL_PATH)

with open(LABELS_PATH, "r") as f:
    class_labels = json.load(f)

# Convert string keys ("0", "1") to integers if needed
class_labels = {int(k): v for k, v in class_labels.items()}
print(f"Model loaded successfully! Recognized classes: {list(class_labels.values())}")


def predict_equipment(image_path):
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    # Load and preprocess image (224x224, normalized to [0, 1])
    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # shape: (1, 224, 224, 3)

    # Predict probabilities
    predictions = model.predict(img_array)[0]
    best_index = int(np.argmax(predictions))
    best_confidence = float(predictions[best_index])
    equipment_name = class_labels[best_index]

    print("\n" + "=" * 50)
    print(f"IMAGE: {image_path}")
    print(f"TOP PREDICTION : {equipment_name.upper()}")
    print(f"CONFIDENCE     : {best_confidence * 100:.2f}%")
    print(f"THRESHOLD (65%): {'PASSED (Accepted)' if best_confidence >= CONFIDENCE_THRESHOLD else 'FLAGGED (Needs manual verification)'}")
    print("=" * 50)

    # Show top 3 rankings
    top_3_indices = np.argsort(predictions)[::-1][:3]
    print("Top-3 Probabilities:")
    for rank, idx in enumerate(top_3_indices, 1):
        print(f"  {rank}. {class_labels[idx]}: {predictions[idx] * 100:.2f}%")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_img = sys.argv[1]
    else:
        print("\nUsage: python test_recognition.py <path_to_image>")
        print("Example: python test_recognition.py sample.jpg")
        sys.exit(0)

    predict_equipment(test_img)
