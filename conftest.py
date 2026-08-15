"""
Ensures the project root AND each pipeline subfolder are on sys.path before
any test module is collected, so `from verifier import ...`, `from router
import ...`, `from fixtures import ...`, etc. all resolve reliably —
mirroring the same sys.path setup app.py does for itself.

This file must live at the project root:
    C:\\project_codes\\clerk\\conftest.py
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Root itself — this is where fixtures.py belongs.
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Same four subfolders app.py adds to its own sys.path.
for _folder in ("retrieval", "generation", "routing", "ingestion"):
    _path = os.path.join(PROJECT_ROOT, _folder)
    if os.path.isdir(_path) and _path not in sys.path:
        sys.path.insert(0, _path)