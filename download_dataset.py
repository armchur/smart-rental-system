"""
Smart Rental System - Dataset Downloader using Bing
Downloads clean images for the 8 rental equipment classes.
"""
import os
import shutil
from bing_image_downloader import downloader

CLASSES = [
    "portable petrol generator",
    "portable concrete mixer machine",
    "portable inverter welding machine",
    "cordless electric hand drill",
    "gasoline water pump portable",
    "chainsaw petrol wood cutting",
    "lawn mower grass cutter",
    "portable air compressor tank"
]

FOLDER_NAMES = [
    "generator",
    "concrete_mixer",
    "welding_machine",
    "electric_drill",
    "water_pump",
    "chainsaw",
    "lawn_mower",
    "air_compressor"
]

TEMP_DIR = "dataset_raw"

print("Starting image download from Bing...")

for query, folder_name in zip(CLASSES, FOLDER_NAMES):
    print(f"\nDownloading images for: {folder_name} (query: '{query}')...")
    downloader.download(
        query,
        limit=50,
        output_dir=TEMP_DIR,
        adult_filter_off=True,
        force_replace=False,
        timeout=10,
        verbose=False
    )
    
    # Organize into dataset/train (80%) and dataset/val (20%)
    source_folder = os.path.join(TEMP_DIR, query)
    if os.path.exists(source_folder):
        images = [f for f in os.listdir(source_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        for i, img in enumerate(images):
            split = "train" if (i % 5 != 0) else "val"
            dest_dir = os.path.join("dataset", split, folder_name)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(os.path.join(source_folder, img), os.path.join(dest_dir, f"{folder_name}_{i+1:03d}.jpg"))
        print(f"  Organized {len(images)} images into dataset/train and dataset/val for '{folder_name}'.")

# Clean up temporary raw download folder
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR)

print("\n" + "="*50)
print("ALL DOWNLOADS COMPLETE AND ORGANIZED!")
print("Check your 'dataset/train' and 'dataset/val' folders.")
print("="*50)
