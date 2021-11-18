from typing import *

import re
from web3 import Web3
from web3.types import Nonce

from pyout import consts


class Address:
    """A prefix agnostic Ronin wallet address."""

    hex_part: str

    @property
    def p_0x(self) -> str:
        return "0x" + self.hex_part

    @property
    def p_ronin(self) -> str:
        return "ronin:" + self.hex_part

    def __init__(self, address: str):
        matches = re.match(r"^(?:ronin:|0x)?([0-9A-Fa-f]{40})$", address)
        if not matches:
            raise ValueError(f"Invalid address {address}.")

        self.hex_part = matches.group(1)

    def __str__(self) -> str:
        return self.p_0x


def get_nonce(address: Address) -> Nonce:
    """Returns the number of confirmed transaction sent by this account. Used
    for letting miners know the order of transactions."""

    w3 = Web3(
        Web3.HTTPProvider(
            consts.RONIN_PROVIDER_FREE,
            request_kwargs={
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": consts.USER_AGENT,
                }
            },
        )
    )
    nonce = w3.eth.get_transaction_count(Web3.toChecksumAddress(address.p_0x))

    return nonce


def check_balance(address: Address) -> int:
    """Returns the (claimed) SLP balance of address."""
    w3 = Web3(
        Web3.HTTPProvider(
            consts.RONIN_PROVIDER,
            request_kwargs={
                "headers": {
                    "Content-Type": "application/json",
                    "User-Agent": consts.USER_AGENT,
                }
            },
        )
    )
    contract = w3.eth.contract(
        address=Web3.toChecksumAddress(consts.SLP_CONTRACT_ADDRESS),
        abi=__make_balance_abi(),
    )

    balance = contract.functions.balanceOf(
        Web3.toChecksumAddress(address.p_0x)
    ).call()

    return int(balance)


def __make_balance_abi() -> Any:
    return [
        {
            "constant": True,
            "inputs": [
                {"internalType": "address", "name": "", "type": "address"}
            ],
            "name": "balanceOf",
            "outputs": [
                {"internalType": "uint256", "name": "", "type": "uint256"}
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        }
    ]
