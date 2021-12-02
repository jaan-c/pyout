from typing import *

import os
import platform
import logging
import sys

from pyout import config
from pyout import claims
from pyout import ronin
from pyout import send

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("pyout_output.txt"),
        logging.StreamHandler(sys.stdout),
    ],
)


def main() -> None:
    payouts = config.load_file("pyout_config.json")

    logging.info("### SCHOLAR ACCOUNT CLAIM START")
    for p in payouts:
        logging.info(f"Claiming for {p.player_name} ({p.scholar_address}):")

        balance = ronin.get_balance(p.scholar_address)
        unclaimed_slp = claims.get_unclaimed_slp(p.scholar_address)
        logging.info(f"\tInitial Balance: {balance}")
        logging.info(f"\tInitial Unclaimed SLP: {unclaimed_slp}")

        if unclaimed_slp != 0:
            logging.info(f"\tClaiming...")
            claims.claim_slp(p.scholar_address, p.scholar_private_key)
            logging.info(f"Done!")

            balance = ronin.get_balance(p.scholar_address)
            unclaimed_slp = claims.get_unclaimed_slp(p.scholar_address)
            logging.info(f"\tEnd Balance: {balance}")
            logging.info(f"\tEnd Unclaimed SLP: {unclaimed_slp}")
        else:
            logging.info("\tNothing to claim! Skipping!")

    logging.info("### PAYOUT START")
    for p in payouts:
        balance = ronin.get_balance(p.scholar_address)
        player_cut = round(balance * p.player_percent)
        manager_cut = balance - player_cut

        assert balance == (manager_cut + player_cut)

        scholar_balance = ronin.get_balance(p.scholar_address)
        manager_balance = ronin.get_balance(p.manager_address)
        player_balance = ronin.get_balance(p.player_address)
        logging.info(f"\tInitial Scholar Balance: {scholar_balance}")
        logging.info(f"\tInitial Manager Balance: {manager_balance}")
        logging.info(f"\tInitial Player Balance: {player_balance}")

        logging.info(f"\tSending {manager_cut} SLP from scholar to manager...")
        send.send_slp(
            from_address=p.scholar_address,
            from_private_key=p.scholar_private_key,
            to_address=p.manager_address,
            amount=manager_cut,
            logger_func=logging.info,
            logger_prefix="\t",
        )

        logging.info(f"\tSending {player_cut} SLP from scholar to player...")
        send.send_slp(
            from_address=p.scholar_address,
            from_private_key=p.scholar_private_key,
            to_address=p.player_address,
            amount=player_cut,
            logger_func=logging.info,
            logger_prefix="\t",
        )

        scholar_balance = ronin.get_balance(p.scholar_address)
        manager_balance = ronin.get_balance(p.manager_address)
        player_balance = ronin.get_balance(p.player_address)
        logging.info(f"\tEnd Scholar Balance: {scholar_balance}")
        logging.info(f"\tEnd Manager Balance: {manager_balance}")
        logging.info(f"\tEnd Player Balance: {player_balance}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)

    # If on Windows prevent abruptly closing the CMD window.
    if platform.system() == "Windows":
        os.system("pause")
