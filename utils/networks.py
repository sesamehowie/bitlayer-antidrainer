from dataclasses import dataclass


class Network:
    def __init__(
        self,
        name,
        chain_id,
        rpc_list,
        scanner,
        eip1559_support: bool = False,
        token: str = "ETH",
    ):
        self.name = name
        self.chain_id = chain_id
        self.rpc_list = rpc_list
        self.scanner = scanner
        self.token = token


@dataclass
class Networks:
    Bitlayer = Network(
        name="Bitlayer",
        chain_id=200901,
        rpc_list=[
            "https://rpc.bitlayer-rpc.com",
            "https://rpc.ankr.com/bitlayer",
            "https://rpc.bitlayer.org",
        ],
        scanner="https://www.btrscan.com",
        eip1559_support=True,
        token="BTC",
    )
