from typing import *

import re


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


class Payout:
    manager_address: Address
    scholar_address: Address
    scholar_private_key: str
    player_name: str
    player_address: Address
    player_percent: float

    def __init__(
        self,
        manager_address: Address,
        scholar_address: Address,
        scholar_private_key: str,
        player_name: str,
        player_address: Address,
        player_percent: float,
    ):
        if not (0 <= player_percent <= 1):
            raise ValueError(
                f"player_percent must be between 0 to 1 got {player_percent}"
            )

        self.manager_address = manager_address
        self.scholar_address = scholar_address
        self.scholar_private_key = scholar_private_key
        self.player_name = player_name
        self.player_address = player_address
        self.player_percent = player_percent
