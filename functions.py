import asyncio

from data.config import SLEEP_INTERVAL, SLEEP_ON_RATELIMIT, DEPOSIT_ADDRESS
from models.w3_client import AsyncW3Client
from utils.networks import Networks
from utils.helpers import async_sleep


async def process_account(account_name, private_key, proxy, logger, deposit_address):
    try:
        w3_client = AsyncW3Client(
            account_name, proxy, private_key, Networks.Bitlayer, logger
        )
        w3 = await w3_client.configure_web3_client()

        while True:
            try:
                tx_data = await w3_client.get_tx_data_if_sufficient_balance(
                    w3, deposit_address
                )
                if isinstance(tx_data, dict):
                    await w3_client.sign_and_send_transaction(w3, tx_data)
                await async_sleep(SLEEP_INTERVAL)
            except Exception as e:
                w3_client.logger.info(
                    f"{account_name} - Error on balance check - {str(e)}"
                )
                await async_sleep(SLEEP_ON_RATELIMIT)
                continue
    finally:
        try:
            await w3_client.session.connector.close()
            await w3_client.session.close()
        except Exception:
            pass


def account_wrapper(account_name, private_key, proxy, logger):
    asyncio.run(
        process_account(account_name, private_key, proxy, logger, DEPOSIT_ADDRESS)
    )
