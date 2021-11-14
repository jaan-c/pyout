from eth_account.messages import encode_defunct
import requests
from requests.exceptions import RetryError
from web3 import Web3

from pyout.ronin import Address
from pyout import consts


AXIE_GRAPHQL_URL = "https://graphql-gateway.axieinfinity.com/graphql"


class AxieGraphQlException(Exception):
    pass


def get_jwt(
    session: requests.Session, address: Address, private_key: str
) -> str:
    message = __create_random_message(session)
    signature = Web3().eth.account.sign_message(
        encode_defunct(text=message), private_key=private_key
    )
    payload = {
        "operationName": "CreateAccessTokenWithSignature",
        "variables": {
            "input": {
                "mainnet": "ronin",
                "owner": address.p_0x,
                "message": message,
                "signature": signature["signature"].hex(),
            }
        },
        "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!)"
        "{createAccessTokenWithSignature(input: $input) "
        "{newAccount result accessToken __typename}}",
    }

    try:
        response = session.post(
            AXIE_GRAPHQL_URL,
            headers={"User-Agent": consts.USER_AGENT},
            json=payload,
        )
    except RetryError as e:
        raise AxieGraphQlException("failed to get JWT") from e

    if 200 <= response.status_code <= 299:
        json_data = response.json()["data"]
        if json_data.get("createAccessTokenWithSignature") and json_data[
            "createAccessTokenWithSignature"
        ].get("accessToken"):
            return json_data["createAccessTokenWithSignature"]["accessToken"]
        else:
            raise AxieGraphQlException(
                f"failed to get JWT, private key may be wrong for account {address.p_0x}"
            )
    else:
        raise AxieGraphQlException(
            f"unexpected response {response.status_code}: {response.content.decode()}"
        )


def __create_random_message(session: requests.Session) -> str:
    payload = {
        "operationName": "CreateRandomMessage",
        "variables": {},
        "query": r"mutation CreateRandomMessage{createRandomMessage}",
    }

    try:
        response = session.post(AXIE_GRAPHQL_URL, json=payload)
    except RetryError as e:
        raise AxieGraphQlException("failed to get random message") from e

    if 200 <= response.status_code <= 299:
        return response.json()["data"]["createRandomMessage"]
    else:
        raise AxieGraphQlException(
            f"unexpected response {response.status_code}"
        )
