import sys
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from functions import account_wrapper
from models.logger import configure_logger
from utils.file_utils import read_txt


def main():
    configure_logger("logs/")
    private_keys = read_txt("input_data/private_keys.txt")
    proxies = read_txt("input_data/proxies.txt")

    private_keys_amt = len(private_keys)
    proxies_amt = len(proxies)

    logger.info(f"Loaded {private_keys_amt} private keys and {proxies_amt} proxies.")

    if private_keys_amt != proxies_amt or private_keys_amt == 0 or proxies_amt == 0:
        logger.info("Amount of private keys and proxies should match. Exiting...")
        sys.exit(1)

    account_names = [str(i) for i in range(private_keys_amt)]
    loggers = [logger for _ in range(private_keys_amt)]

    with ThreadPoolExecutor(max_workers=private_keys_amt) as executor:
        executor.map(account_wrapper, account_names, private_keys, proxies, loggers)


if __name__ == "__main__":
    main()
