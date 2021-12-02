from typing import *

from web3 import Web3, exceptions
from web3.types import Wei
import time
import datetime

from pyout import consts
from pyout import abi
from pyout import ronin
from pyout import domain
from pyout import utils


class SendException(Exception):
    pass


def send_slp(
    from_address: domain.Address,
    from_private_key: str,
    to_address: domain.Address,
    amount: int,
    timeout: datetime.timedelta = datetime.timedelta(minutes=10),
    logger_func: Callable[[str], None] = print,
    logger_prefix: str = "",
) -> None:
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
    contract = w3.eth.contract(
        address=Web3.toChecksumAddress(consts.SLP_CONTRACT_ADDRESS),
        abi=abi.make_slp_abi(),
    )
    nonce = ronin.get_nonce(from_address)
    transaction = contract.functions.transfer(
        Web3.toChecksumAddress(to_address.p_0x), amount
    ).buildTransaction(
        {
            "chainId": 2020,
            "gas": Wei(246437),
            "gasPrice": Wei(0),
            "nonce": nonce,
        }
    )
    signature = w3.eth.account.sign_transaction(
        transaction, private_key=from_private_key
    )

    w3.eth.send_raw_transaction(signature.rawTransaction)

    transaction_hash = w3.toHex(w3.keccak(signature.rawTransaction))

    for count in utils.countdown(timeout):
        logger_func(f"{logger_prefix}Awaiting receipt ({count}/{timeout})")
        try:
            receipt = w3.eth.get_transaction_receipt(transaction_hash)
            if receipt["status"] == 1:
                return
            else:
                raise SendException(
                    f"transaction failed for account {from_address} -> {to_address}"
                )
        except exceptions.TransactionNotFound:
            time.sleep(10)
    else:
        raise SendException(
            f"transaction timed out for account {from_address} -> {to_address} (nonce: {nonce})"
        )
