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
