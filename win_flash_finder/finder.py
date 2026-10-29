import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Set

SPECIAL_PRESETS: Dict[str, List[str]] = {
    "pdf": [".pdf"],
    "pth": [".pth"],
    "docs": [".docx", ".doc", ".pdf", ".rtf", ".txt", ".odt", ".xlsx", ".pptx"],
    "code": [".py", ".pyw", ".js", ".ts", ".rs", ".go", ".c", ".cpp", ".h", ".cs", ".java"],
    "archive": [".zip", ".tar", ".gz", ".7z", ".rar", ".bz2"],
}

class FlashFinder:
    """An ultra-fast multithreaded file search utility for scanning directories and filtering by presets, extensions, or regex patterns."""

    def __init__(self, max_workers: int = 16, skip_hidden: bool = True) -> None:
        """Initialize the FlashFinder.

        Args:
            max_workers: Maximum number of worker threads to use for concurrent scanning.
            skip_hidden: Whether to skip hidden and system files/directories.
        """
        self.max_workers: int = max_workers
        self.skip_hidden: bool = skip_hidden

    def _scan_dir(
        self, 
        directory: str, 
        extensions: Optional[Set[str]], 
        pattern: Optional[re.Pattern], 
        depth: int, 
        max_depth: int
    ) -> List[Dict[str, Any]]:
        """Recursively scan a directory using a thread pool for subdirectories.

        Args:
            directory: The directory path to scan.
            extensions: A set of file extensions to filter by.
            pattern: A compiled regular expression pattern to match filenames.
            depth: Current recursion depth.
            max_depth: Maximum recursion depth allowed (-1 for unlimited).

        Returns:
            A list of dictionaries containing file metadata (path, name, size, mtime, extension).
        """
        results: List[Dict[str, Any]] = []
        if max_depth != -1 and depth > max_depth:
            return results

        subdirs: List[str] = []
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

    def find(
        self, 
        root_dir: str, 
        target_preset: Optional[str] = None, 
        ext_list: Optional[List[str]] = None, 
        pattern_str: Optional[str] = None, 
        max_depth: int = -1
    ) -> List[Dict[str, Any]]:
        """Search for files starting from a root directory using optional presets, extensions, or name patterns.

        Args:
            root_dir: The root directory to start searching from.
            target_preset: A specialized preset key (e.g., 'pdf', 'docs', 'code').
            ext_list: An optional list of specific file extensions to filter by.
            pattern_str: An optional regular expression string pattern to match filenames.
            max_depth: Maximum recursion depth (-1 for unlimited).

        Returns:
            A list of matching file records.
        """
        extensions: Set[str] = set()
        if target_preset and target_preset in SPECIAL_PRESETS:
            extensions.update(SPECIAL_PRESETS[target_preset])
        if ext_list:
            for e in ext_list:
                e = e.lower()
                if not e.startswith('.'):
                    e = '.' + e
                extensions.add(e)

        ext_filter: Optional[Set[str]] = extensions if extensions else None
        pattern: Optional[re.Pattern] = re.compile(pattern_str, re.IGNORECASE) if pattern_str else None
        root_path = os.path.abspath(root_dir)
        return self._scan_dir(root_path, ext_filter, pattern, depth=0, max_depth=max_depth)
