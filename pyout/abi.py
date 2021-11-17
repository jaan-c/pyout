from typing import *


def make_slp_abi() -> Any:
    return [
        {
            "constant": False,
            "inputs": [
                {
                    "internalType": "address",
                    "name": "_owner",
                    "type": "address",
                },
                {
                    "internalType": "uint256",
                    "name": "_amount",
                    "type": "uint256",
                },
                {
                    "internalType": "uint256",
                    "name": "_createdAt",
                    "type": "uint256",
                },
                {
                    "internalType": "bytes",
                    "name": "_signature",
                    "type": "bytes",
                },
            ],
            "name": "checkpoint",
            "outputs": [
                {
                    "internalType": "uint256",
                    "name": "_balance",
                    "type": "uint256",
                }
            ],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function",
        },
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
        },
        {
            "constant": False,
            "inputs": [
                {"internalType": "address", "name": "_to", "type": "address"},
                {
                    "internalType": "uint256",
                    "name": "_value",
                    "type": "uint256",
                },
            ],
            "name": "transfer",
            "outputs": [
                {"internalType": "bool", "name": "_success", "type": "bool"}
            ],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function",
        },
    ]
