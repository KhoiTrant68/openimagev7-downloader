import os
import fiftyone as fo
import fiftyone.zoo as foz

ZOO_DIR = "./fiftyone_cache"     
OUTPUT_ROOT = "./dataset"        
DATASET_NAME = "open-images-v7"
MAP_RANGE = {"train": (10, 20), "validation": (1, 5)}

fo.config.dataset_zoo_dir = ZOO_DIR

os.makedirs(OUTPUT_ROOT, exist_ok=True)
print(f"🚀 Initializing download to {ZOO_DIR}...")

for split, (start_idx, end_idx) in MAP_RANGE.items():
    print(f"\n📥 Fetching {split} up to index {end_idx}...")

    dataset = foz.load_zoo_dataset(
        DATASET_NAME,
        split=split,
        max_samples=end_idx,
        shuffle=False,
        label_types=[], 
    )

    view = dataset.skip(start_idx)
    
    final_split_name = "valid" if split == "validation" else split
    out_dir = os.path.join(OUTPUT_ROOT, final_split_name)
    os.makedirs(out_dir, exist_ok=True)

    print(f"🔗 Linking files to {out_dir} (0 extra disk space used)...")
    
    for sample in view:
        src = sample.filepath
        fname = os.path.basename(src)
        dst = os.path.join(out_dir, fname)
        
        # Only link if the file doesn't already exist in the destination
        if not os.path.exists(dst):
            try:
                # First attempt: Hard Link (Acts like a real file, uses 0 extra space)
                os.link(src, dst)
            except OSError:
                # Fallback: Symbolic Link (Shortcut) if hard linking fails 
                # (e.g., if ZOO_DIR and OUTPUT_ROOT are on different hard drives)
                os.symlink(src, dst)

    dataset.delete()

print(f"\n✅ All images successfully linked to {OUTPUT_ROOT}!")