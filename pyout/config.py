from typing import *

import json
import jsonschema

from pyout import domain


def load_file(config_path: str) -> List[domain.Payout]:
    with open(config_path) as f:
        content = f.read()

    return load_string(content)


def load_string(string: str) -> List[domain.Payout]:
    json_config = json.loads(string)

    jsonschema.validate(json_config, __CONFIG_SCHEMA)

    payouts: List[domain.Payout] = []
    for payout_raw in json_config["payouts"]:
        payout = domain.Payout(
            manager_address=domain.Address(json_config["manager_address"]),
            scholar_address=domain.Address(payout_raw["scholar_address"]),
            scholar_private_key=payout_raw["scholar_private_key"],
            player_name=payout_raw["player_name"],
            player_address=domain.Address(payout_raw["player_address"]),
            player_percent=payout_raw["player_percent"] / 100,
        )

        payouts.append(payout)

    return payouts


__CONFIG_SCHEMA = {
    "type": "object",
    "required": ["manager_address", "payouts"],
    "properties": {
        "manager_address": {
            "type": "string",
            "pattern": "^(ronin:|0x)?([0-9A-Fa-f]{40})$",
        },
        "payouts": {
            "type": "array",
            "items": {
                "properties": {
                    "scholar_address": {
                        "type": "string",
                        "pattern": "^(ronin:|0x)?([0-9A-Fa-f]{40})$",
                    },
                    "scholar_private_key": {
                        "type": "string",
                    },
                    "player_name": {
                        "type": "string",
                    },
                    "player_address": {
                        "type": "string",
                        "pattern": "^(ronin:|0x)?([0-9A-Fa-f]{40})$",
                    },
                    "player_percent": {
                        "type": "integer",
                        "exclusiveMinimum": 0,
                        "exclusiveMaximum": 100,
                    },
                }
            },
        },
    },
}
