"""Shared logging setup without logging user message contents."""

import logging


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
