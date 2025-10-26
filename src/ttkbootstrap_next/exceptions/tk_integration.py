import logging
from ttkbootstrap_next.exceptions.base import UIError, LayoutError

log = logging.getLogger(__name__)


def normalize_tcl_error(e: BaseException) -> UIError:
    msg = str(e).lower()
    if "geometry manager" in msg:
        return LayoutError("Incompatible geometry managers for this parent.")
    if "bad window path name" in msg:
        return UIError("Widget no longer exists (was destroyed).")
    if "unknown option" in msg:
        return UIError("Unknown widget option; check the option name.")
    return UIError(f"Toolkit error: {str(e) or e.__class__.__name__}")
