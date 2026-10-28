import argparse
import os
import sys
import time
from win_flash_finder.finder import FlashFinder, SPECIAL_PRESETS

def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def main():
    parser = argparse.ArgumentParser(
        description="Ultra-fast Windows file and folder finder CLI tool with specialized instant presets."
    )
    parser.add_argument("root", nargs="?", default=".", help="Root directory to start searching (default: current directory)")
    parser.add_argument("-p", "--preset", choices=list(SPECIAL_PRESETS.keys()), help="Specialized finder preset (pdf, pth, docs, code, archive)")
    parser.add_argument("-e", "--ext", action="append", help="File extension to filter by (e.g., txt, .py)")
    parser.add_argument("-n", "--name", help="Regex or string pattern to match in filename")
    parser.add_argument("-d", "--max-depth", type=int, default=-1, help="Maximum recursion depth (-1 for unlimited)")
    parser.add_argument("-w", "--workers", type=int, default=16, help="Number of worker threads (default: 16)")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders")
    parser.add_argument("--summary", action="store_true", help="Show summary stats only")

    args = parser.parse_args()

    if not os.path.exists(args.root):
        print(f"Error: Path '{args.root}' does not exist.", file=sys.stderr)
        sys.exit(1)

    finder = FlashFinder(max_workers=args.workers, skip_hidden=not args.include_hidden)

    start_time = time.time()
    results = finder.find(
        root_dir=args.root,
        target_preset=args.preset,
        ext_list=args.ext,
        pattern_str=args.name,
        max_depth=args.max_depth
    )
    elapsed = time.time() - start_time

    if not args.summary:
        for item in results:
            size_str = format_size(item['size'])
            print(f"{item['path']}\t[{size_str}]")

    print(f"\nFound {len(results)} file(s) in {elapsed:.3f} seconds.")

if __name__ == "__main__":
    main()
