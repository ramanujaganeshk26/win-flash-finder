import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Set

SPECIAL_PRESETS = {
    "pdf": [".pdf"],
    "pth": [".pth"],
    "docs": [".docx", ".doc", ".pdf", ".rtf", ".txt", ".odt", ".xlsx", ".pptx"],
    "code": [".py", ".pyw", ".js", ".ts", ".rs", ".go", ".c", ".cpp", ".h", ".cs", ".java"],
    "archive": [".zip", ".tar", ".gz", ".7z", ".rar", ".bz2"],
}

class FlashFinder:
    def __init__(self, max_workers: int = 16, skip_hidden: bool = True):
        self.max_workers = max_workers
        self.skip_hidden = skip_hidden

    def _scan_dir(self, directory: str, extensions: Optional[Set[str]], pattern: Optional[re.Pattern], depth: int, max_depth: int) -> List[Dict[str, Any]]:
        results = []
        if max_depth != -1 and depth > max_depth:
            return results

        subdirs = []
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        if self.skip_hidden and entry.name.startswith(("$", ".")):
                            continue

                        if entry.is_dir(follow_symlinks=False):
                            subdirs.append(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            name = entry.name
                            ext = os.path.splitext(name)[1].lower()

                            if extensions and ext not in extensions:
                                continue
                            if pattern and not pattern.search(name):
                                continue

                            stat = entry.stat()
                            results.append({
                                "path": entry.path,
                                "name": name,
                                "size": stat.st_size,
                                "mtime": stat.st_mtime,
                                "extension": ext
                            })
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            return results

        if subdirs and (max_depth == -1 or depth < max_depth):
            workers = min(len(subdirs), self.max_workers) or 1
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [
                    executor.submit(self._scan_dir, sd, extensions, pattern, depth + 1, max_depth)
                    for sd in subdirs
                ]
                for future in as_completed(futures):
                    results.extend(future.result())

        return results

    def find(self, root_dir: str, target_preset: Optional[str] = None, ext_list: Optional[List[str]] = None, pattern_str: Optional[str] = None, max_depth: int = -1) -> List[Dict[str, Any]]:
        extensions = set()
        if target_preset and target_preset in SPECIAL_PRESETS:
            extensions.update(SPECIAL_PRESETS[target_preset])
        if ext_list:
            for e in ext_list:
                e = e.lower()
                if not e.startswith('.'):
                    e = '.' + e
                extensions.add(e)

        ext_filter = extensions if extensions else None
        pattern = re.compile(pattern_str, re.IGNORECASE) if pattern_str else None
        root_path = os.path.abspath(root_dir)
        return self._scan_dir(root_path, ext_filter, pattern, depth=0, max_depth=max_depth)
