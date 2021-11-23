from typing import *

import asyncio
import requests
from requests.exceptions import RetryError
from requests.adapters import HTTPAdapter
from web3 import Web3, exceptions
from web3.types import Wei
from urllib3.util import Retry

from pyout import ronin
from pyout import consts
from pyout import axieql
from pyout import abi
from pyout import domain


class ClaimException(Exception):
    pass


async def claim_slp(address: domain.Address, private_key: str) -> None:
    session = __make_session()

    unclaimed_balance = get_unclaimed_slp(address)
    if unclaimed_balance == 0:
        return

    try:
        jwt = axieql.get_jwt(session, address, private_key)
    except axieql.AxieGraphQlException as e:
        raise ClaimException("failed to get JWT") from e

    try:
        url = f"https://game-api.skymavis.com/game-api/clients/{address}/items/1/claim"
        headers = {
            "User-Agent": consts.USER_AGENT,
            "Authorization": f"Bearer {jwt}",
        }
        response = session.post(url, headers=headers)
    except RetryError as e:
        raise ClaimException(
            f"failed to claim SLP for account {address}"
        ) from e

    if response.status_code not in range(200, 300):
        raise ClaimException(
            f"unexpected response {response.status_code}: {response.content.decode()}"
        )

    signature = response.json().get("blockchain_related", {}).get("signature")
    if not signature:
        raise ClaimException(
            f"response returned no signature for account {address}"
        )
    nonce = ronin.get_nonce(address)
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
    slp_contract = w3.eth.contract(
        address=Web3.toChecksumAddress(consts.SLP_CONTRACT_ADDRESS),
        abi=abi.make_slp_abi(),
    )
    claim = slp_contract.functions.checkpoint(
        Web3.toChecksumAddress(address.p_0x),
        signature["amount"],
        signature["timestamp"],
        signature["signature"],
    ).buildTransaction({"gas": Wei(492874), "gasPrice": Wei(0), "nonce": nonce})
    signed_claim = w3.eth.account.sign_transaction(
        claim, private_key=private_key
    )

    w3.eth.send_raw_transaction(signed_claim.rawTransaction)

    # Wait for transaction to finish.
    transaction_hash = w3.toHex(w3.keccak(signed_claim.rawTransaction))
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(transaction_hash)
            if receipt["status"] != 1:
                raise ClaimException(
                    f"claim transaction failed for account {address}"
                )
        except exceptions.TransactionNotFound as e:
            await asyncio.sleep(5)


def get_unclaimed_slp(address: domain.Address) -> int:
    session = __make_session()

    url = f"https://game-api.skymavis.com/game-api/clients/{address}/items/1"

    try:
        response = session.get(url, headers={"User-Agent": consts.USER_AGENT})
    except RetryError as e:
        raise ClaimException("failed to check unclaimed SLP") from e

    if 200 <= response.status_code <= 299:
        return int(response.json()["total"])
    else:
        raise ClaimException(
            f"unexpected response {response.status_code}: {response.content.decode()}"
        )


def __make_session() -> requests.Session:
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods={"GET", "POST"},
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retries))

    return session
