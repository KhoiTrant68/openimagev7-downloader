import os
import argparse
import fiftyone as fo
import fiftyone.zoo as foz

def main():
    parser = argparse.ArgumentParser(description="Efficiently download and link FiftyOne Zoo datasets.")

    # Paths
    parser.add_argument("--zoo-dir", type=str, default="./fiftyone_cache", help="Directory to store the raw zoo cache")
    parser.add_argument("--out-dir", type=str, default="./dataset", help="Root directory for the linked dataset")
    
    # Dataset Config
    parser.add_argument("--dataset", type=str, default="open-images-v7", help="Name of the dataset in the FiftyOne Zoo")
    
    # Range Config (Passed as strings like "10:20")
    parser.add_argument("--train-range", type=str, default="10:20", help="Range for train split (start:end)")
    parser.add_argument("--val-range", type=str, default="1:5", help="Range for validation split (start:end)")

    args = parser.parse_args()

    # Configure FiftyOne
    fo.config.dataset_zoo_dir = args.zoo_dir
    os.makedirs(args.out_dir, exist_ok=True)

    # Process ranges
    def parse_range(r_str):
        start, end = map(int, r_str.split(':'))
        return start, end

    map_range = {
        "train": parse_range(args.train_range),
        "validation": parse_range(args.val_range)
    }

    print(f"🚀 Initializing download to {args.zoo_dir}...")

    for split, (start_idx, end_idx) in map_range.items():
        print(f"\n📥 Fetching {split} (Indices {start_idx} to {end_idx})...")

        # Load from zoo (we fetch up to end_idx to ensure we have the full range available)
        dataset = foz.load_zoo_dataset(
            args.dataset,
            split=split,
            max_samples=end_idx,
            shuffle=False,
            label_types=[], 
        )

        # Create the specific view
        view = dataset.skip(start_idx)
        
        # Determine output folder name
        split_folder = "valid" if split == "validation" else split
        target_path = os.path.join(args.out_dir, split_folder)
        os.makedirs(target_path, exist_ok=True)

        print(f"🔗 Linking {len(view)} files to {target_path}...")
        
        for sample in view:
            src = sample.filepath
            fname = os.path.basename(src)
            dst = os.path.join(target_path, fname)
            
            if not os.path.exists(dst):
                try:
                    # Hard link: Zero extra space, looks like a real file
                    os.link(src, dst)
                except OSError:
                    # Symlink: Cross-drive fallback
                    os.symlink(src, dst)

        # Cleanup local DB reference to keep it lightweight
        dataset.delete()

    print(f"\n✅ Done! Images are ready in: {os.path.abspath(args.out_dir)}")

if __name__ == "__main__":
    main()