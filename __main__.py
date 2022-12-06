#!/usr/bin/env python
import os
import sys
import json
import subprocess
import requests
import time
import toml
from __init__ import bcolors, __location__

try:
    f = open(os.path.join(__location__, ".config.toml"))
    config = toml.loads(f.read())
    settings = config['settings']
except FileNotFoundError:
    print(f"{bcolors.red}error{bcolors.nc}: config file not found.\n\n"
    f"quick setup:\n\n  1. {bcolors.blue}cp ./multisigner/config.toml ./multisigner/.config.toml{bcolors.nc}\n"
    f"  2. {bcolors.blue}nano multisigner/.config.toml{bcolors.nc} and fill in your info\n  3. run this program again\n")
    exit()

txs = sys.argv[1:]
if txs == []:
    print(f"{bcolors.red}error: no txs provided {bcolors.nc}(select transactions like 'python3 multisigner 0 1' for transactions 0 and 1)")
    exit()
try: NAME = subprocess.check_output(["git", "config", "user.name"]).decode("utf-8").strip()
except subprocess.CalledProcessError: NAME=""
try : acct = json.loads(subprocess.check_output(
    [ "osmosisd", "q", "account", settings['KEY'], "--node", settings['RPC'], "--output", "json" ]).decode("utf-8"))["account_number"]
except subprocess.CalledProcessError:
    print(f"{bcolors.red}rpc error. please check your connection, try a different node, or wait and try again")
    exit()
if NAME:
    FILE = f"-{NAME}-sig.json"
else:
    print("\ngit not installed. txs will be printed, not uploaded")
    FILE = "-sig.json"

for tx in txs:
    r = requests.get(
            f"https://raw.githubusercontent.com/{settings['REPO']}/main/transactions/unsigned/{tx}.json"
        )
    with open(f"/tmp/{tx}.json", "w") as f:
            f.write(r.text)
    print(f"\nplease check tx {bcolors.blue}{tx}{bcolors.nc} before signing:\n")
    with open(f"/tmp/{tx}.json") as f:
        print(bcolors.yellow + json.dumps(json.load(f)["body"]["messages"], indent=1) + f"\n{bcolors.nc}")
    subprocess.check_output(
        [ "osmosisd", "tx", "sign", f"/tmp/{tx}.json", "--from", settings['KEY'], "--keyring-backend", settings['KEYRING'], "--account-number", acct,
        "--sequence", tx, "--chain-id", settings['CHAIN'], "--offline", "--output-document", f"/tmp/{tx}{FILE}" ])

signed = []
for tx in txs:
    if os.path.isfile(f"/tmp/{tx}{FILE}"):
        os.rename(f"/tmp/{tx}{FILE}", f"./transactions/signatures/{tx}{FILE}")
        signed.append(tx)

if signed:
   if NAME:
      choice = input("signatures completed\n\n   1 to upload signatures to repo\n   2 to print signatures to console\n\nyour choice: ")
      while choice != "1" and choice != "2":
         time.sleep(0.1)
         choice = input("invalid input. please enter 1 to upload or 2 to print signatures: ")
   else:
      choice = "2"
else:
    print("error: no signatures found")
    exit()

if choice == "1":
    try:
        subprocess.check_output(["git", "add", "."])
        subprocess.check_output(["git", "commit", "-m", f"{NAME} signed ' '.join(signed)"])
        subprocess.check_output(["git", "push"])
        print(f"\n{bcolors.green}signatures uploaded to repo{bcolors.nc}")
    except subprocess.CalledProcessError:
        print(f"{bcolors.red}error uploading signatures to repo{bcolors.nc}")
elif choice == "2":
   print(f"\nprinting signatures now. you can copy and paste this output")
   time.sleep(1)
   for sig in signed:
     with open(f"./transactions/signatures/{sig}{FILE}") as f:
        print(f"{bcolors.magenta}\n----------------------sig {bcolors.blue}{sig}{bcolors.magenta} begins----------------------\n{bcolors.grey}" + json.dumps(json.load(f), indent=1) +
        f"{bcolors.magenta}\n----------------------sig {bcolors.blue}{sig}{bcolors.magenta} ends----------------------{bcolors.nc}")
else:
   print("fatal error")
   exit()

def main ():
    pass

if __name__ == '__main__':
    main()
