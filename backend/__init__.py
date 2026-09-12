"""Varidhi SIH 2026 Marine Intelligence Backend Package."""

import os
import sys

# Ensure backend/vendor is available in sys.path if present
_vendor_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "vendor"))
if os.path.isdir(_vendor_dir) and _vendor_dir not in sys.path:
    sys.path.insert(0, _vendor_dir)

# Ensure project root is in sys.path
_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
