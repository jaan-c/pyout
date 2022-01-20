# pyout

A script for automating SLP payout of Axie scholars.

# How to Setup

Clone or download the repository. Activate `venv`:

    source bin/activate

Install all dependencies:

    pip3 install -r requirements.txt

# How to Run

First create a config file for the program at the root of the project folder, name it `pyout_config.json`, and in the file follow this schema:

    {
        "manager_address": "[RONIN ADDRESS]",
        "payouts": [
            {
                "scholar_address": "[RONIN ADDRESS]",
                "scholar_private_key": "[PRIVATE KEY]",
                "player_name": "[SCHOLAR NAME]",
                "player_address": "[RONIN ADDRESS]",
                "player_percent": 40
            },
            {
                "scholar_address": "[RONIN ADDRESS]",
                "scholar_private_key": "[PRIVATE KEY]",
                "player_name": "[SCHOLAR NAME]",
                "player_address": "[RONIN ADDRESS]",
                "player_percent": 45
            }
        ]
    }

- `manager_address` is where `(100 - player_percent)%` of each `scholar_address` SLP earning is sent.
- `payouts` contains a list of scholar and corresponding player addresses.
  - `scholar_address` is the address that is controlled by the manager, one that earns the SLP and contains the actual Axies.
  - `scholar_private_key` is the key you obtain from Ronin Wallet, used for authentication.
  - `player_name`'s only purpose is to label the logs.
  - `player_address` is the wallet address of the person who plays the scholar account, receives `player_percent` of the SLP earned by `scholar_address`.
  - `player_percent` specifies the percent of scholar account earning that is sent to `player_address`. Must be an integer in 0-100 range.

After creating the config file, run the program:

    python3 -m pyout

# Notes

I recommend running the program locally with user supervision. The program runs by first *claiming* earned SLPs, then sending them out, first to the manager and then the players. The program will abort on any errors, and `pyout_output.txt` is always created containing a copy of logs from when the program is last ran.