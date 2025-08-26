import asyncio
import pyuseragents

from aiohttp import ClientTimeout, ClientSession
from aiohttp_socks import ProxyConnector
from eth_account import Account
from python_socks import ProxyType
from web3 import AsyncWeb3
from web3.providers.rpc.async_rpc import AsyncHTTPProvider
from web3.eth import AsyncEth


class AsyncW3Client:
    def __init__(self, acc_id, proxy, private_key, network, logger):
        self.id = acc_id
        self.proxy = proxy
        self.private_key = private_key
        self.network = network
        self.logger = logger
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address
        self.user_agent = pyuseragents.random()
        self.provider, self.session = self.get_provider_and_session()

    def process_proxy(self):
        self.logger.info(f"{self.id} - Formatting proxy...")

        user_pass, ip_port = self.proxy.split("@")
        user, password = [item.strip() for item in user_pass.split(":")]
        ip, port = [item.strip() for item in ip_port.split(":")]

        return user, password, ip, port

    def get_provider_and_session(self):
        self.logger.info(f"{self.id} - Setting up provider and session...")

        try:
            user, password, ip, port = self.process_proxy()

            provider = AsyncHTTPProvider(
                endpoint_uri=self.network.rpc_list[0],
                request_kwargs={
                    "headers": {
                        "Content-Type": "application/json",
                        "User-Agent": self.user_agent,
                    },
                },
            )
            session = ClientSession(
                connector=ProxyConnector(
                    proxy_type=ProxyType.HTTP,
                    host=ip,
                    port=port,
                    username=user,
                    password=password,
                ),
                timeout=ClientTimeout(sock_connect=60, sock_read=60, total=120),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": self.user_agent,
                },
            )

            return provider, session
        except Exception as e:
            self.logger.error(f"Exception: {str(e)}")
            return None, None

    async def configure_web3_client(self):
        self.logger.info(f"{self.id} - Configuring Web3 Client...")

        await self.provider.cache_async_session(self.session)
        w3 = AsyncWeb3(self.provider, modules={"eth": (AsyncEth,)})
        return w3

    async def get_balance(self, w3: AsyncWeb3):
        self.logger.info(f"{self.id} - Getting balance for address {self.address} ...")

        try:
            balance = int(await w3.eth.get_balance(self.address))
            return balance
        except Exception as e:
            self.logger.warning(
                f"{self.id} - {self.address} - Failed to get balance: {str(e)}"
            )
            return 0

    async def get_transaction_fee(self, w3: AsyncWeb3):
        self.logger.info(f"{self.id} - Retrieving fee data...")

        fee_dict = {"gas": 21500}

        for attempt in range(3):
            try:
                gas_price = int(int(await w3.eth.gas_price) * 1.02)
                if gas_price:
                    fee_dict |= {"gasPrice": gas_price}
                    break
            except Exception as e:
                self.logger.error(f"Failed to get gas price: {str(e)}")
                await asyncio.sleep(5)
                if attempt >= 2:
                    fee_dict |= {"gasPrice": 0}

        return fee_dict

    async def get_tx_data_if_sufficient_balance(
        self, w3: AsyncWeb3, deposit_address: str
    ):
        self.logger.info(
            f"{self.id} - Waiting for balance to generate transaction data..."
        )

        balance = await self.get_balance(w3)
        fee = await self.get_transaction_fee(w3)

        if fee["gasPrice"] == 0:
            fee["gasPrice"] = int(int(await w3.eth.gas_price) * 1.05)

        total_fee = fee["gas"] * fee["gasPrice"]
        if balance > total_fee:
            self.logger.info(
                f"{self.id} - address {self.address} has enough balance to transfer tokens, creating transaction..."
            )

            tx_data = {
                "from": self.address,
                "to": deposit_address,
                "chainId": self.network.chain_id,
                "gas": fee["gas"],
                "gasPrice": fee["gasPrice"],
                "value": int(balance - total_fee),
                "nonce": await w3.eth.get_transaction_count(self.address),
            }
            return tx_data
        else:
            self.logger.info(
                f"{self.id} - Balance is insufficient to create a native token transfer."
            )
            return None

    async def sign_and_send_transaction(self, w3: AsyncWeb3, tx_data: dict):
        self.logger.info(
            f"{self.id} - Creating transfer of {float(tx_data['value'] / 10 ** self.network.decimals):.6f} {self.network.token}.\nRecipient: {tx_data['to']}.\nNetwork: {self.network.name}"
        )

        try:
            signed = w3.eth.account.sign_transaction(
                transaction_dict=tx_data, private_key=self.private_key
            )

            if signed:
                tx_hash = await w3.eth.send_raw_transaction(signed.raw_transaction)
                if tx_hash:
                    receipt = await w3.eth.wait_for_transaction_receipt(tx_hash.hex())
                    if receipt:
                        self.logger.success(
                            f"{self.id} - Transaction - {self.network.scanner}/tx/{tx_hash.hex()}"
                        )
                        return True

        except Exception as e:
            self.logger.error(f"{self.id} - Transaction error - {str(e)}")
