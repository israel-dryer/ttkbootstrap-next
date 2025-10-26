from __future__ import annotations
import logging
import warnings

# Optional: adapt your existing Logger to the std logging system
try:
    # Your current logger (prints with icons). :contentReference[oaicite:3]{index=3}
    from ttkbootstrap_next.logging.logger import logger as pretty_logger  # rename path as needed
except Exception:
    pretty_logger = None

class PrettyHandler(logging.Handler):
    """Forward logging records to your existing Logger instance."""
    level_map = {
        logging.DEBUG: "debug",
        logging.INFO: "info",
        logging.WARNING: "warning",
        logging.ERROR: "error",
        logging.CRITICAL: "error",
    }
    def emit(self, record: logging.LogRecord):
        if not pretty_logger: return
        msg = self.format(record)
        fn = getattr(pretty_logger, self.level_map.get(record.levelno, "info"))
        # title = logger name; description = message
        fn(record.name, msg)

def setup_logging(debug: bool = False, use_pretty_handler: bool = True) -> logging.Logger:
    log = logging.getLogger("yourlib")  # change to your package name
    log.setLevel(logging.DEBUG if debug else logging.INFO)
    # Clear default handlers (avoid duplicates)
    for h in list(log.handlers):
        log.removeHandler(h)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    if use_pretty_handler and pretty_logger:
        h = PrettyHandler()
    else:
        h = logging.StreamHandler()
        h.setFormatter(fmt)
    h.setLevel(logging.DEBUG if debug else logging.INFO)
    log.addHandler(h)

    # warnings -> logging (so DeprecationWarning etc. land in logs)
    logging.captureWarnings(True)
    warnings.simplefilter("default" if debug else "once", DeprecationWarning)
    return log
