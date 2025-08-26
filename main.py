import os
import sys
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from functions import account_wrapper
from models.logger import configure_logger
from utils.file_utils import read_txt
from data.config import KEYS_PATH, PROXIES_PATH


def main():
    configure_logger("logs/")

    if not os.path.exists(KEYS_PATH) or not os.path.exists(PROXIES_PATH):
        logger.info("Private key and proxy files should exist in the configured path.")
        sys.exit(1)

    private_keys = read_txt(KEYS_PATH)
    proxies = read_txt(PROXIES_PATH)
    private_keys_amt = len(private_keys)
    proxies_amt = len(proxies)

    if private_keys_amt == 0 or proxies_amt == 0:
        logger.info("Private keys and/or proxies amount should not be 0.")
        sys.exit(1)

    logger.info(f"Loaded {private_keys_amt} private keys and {proxies_amt} proxies.")

    if private_keys_amt != proxies_amt:
        logger.info("Amount of private keys and proxies should match.")
        sys.exit(1)

    account_names = [str(i) for i in range(private_keys_amt)]
    loggers = [logger for _ in range(private_keys_amt)]

    with ThreadPoolExecutor(max_workers=private_keys_amt) as executor:
        executor.map(account_wrapper, account_names, private_keys, proxies, loggers)


if __name__ == "__main__":
    main()
