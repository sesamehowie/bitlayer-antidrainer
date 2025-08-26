import sys

from datetime import date
from pathlib import Path

from loguru import logger


def configure_logger(log_path):
    today = date.today().strftime("%d-%m-%y")
    logger.remove(0)

    logger.add(
        Path(log_path + f"/log-{today}.log"),
        level="INFO",
        format="<b>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</b> | <level>{level: <8}</level> | <b>Line {line: >4} ({file}):</b> <b>{message}</b>",
        colorize=False,
        backtrace=True,
        diagnose=True,
    )

    logger.add(
        sink=sys.stdout,
        colorize=True,
        format="<light-cyan>{time:HH:mm:ss}</light-cyan> | <level> {level: <8}</level> | <cyan>{name}</cyan>:<yellow>{function}</yellow> - <white>{message}</white>",
    )
