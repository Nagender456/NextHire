import logging
from pathlib import Path


def configure_logging() -> None:
    log_file = Path(__file__).resolve().parent.parent / "app.log"
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        handlers.append(file_handler)
    except Exception:
        pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=handlers,
        force=True,
    )
