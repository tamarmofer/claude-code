"""Root conftest for pytest - ensures plugin directories are importable."""

import sys
import os

# Add plugin directories to Python path so tests can import from them
plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
if plugins_dir not in sys.path:
    sys.path.insert(0, plugins_dir)

security_hooks_dir = os.path.join(
    os.path.dirname(__file__), "plugins", "security-guidance", "hooks"
)
if security_hooks_dir not in sys.path:
    sys.path.insert(0, security_hooks_dir)
