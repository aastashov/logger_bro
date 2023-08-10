from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if sys.version_info < (3, 10):
    # compatibility for python <3.10
    import importlib_metadata as metadata
else:
    from importlib import metadata

if TYPE_CHECKING:
    from collections.abc import Callable

# The metadata.version that we import for Python 3.7 is untyped, work around
# that.
version: Callable[[str], str] = metadata.version

__version__ = version("ttrack")
