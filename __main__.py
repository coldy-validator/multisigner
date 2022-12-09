#!/usr/bin/env python
import os
import sys
import json
import subprocess
import requests
import time
import toml
from __init__ import bcolors, __location__

def print_sig(signed, file):  # print signatures to console
    print(f"\nprinting signatures now. you can copy and paste this output")
    time.sleep(1)
    for sig in signed:
        with open(f"/tmp/{sig}{file}") as f:
            print(
                f"{bcolors.magenta}\n----------------------sig {bcolors.blue}{sig}{bcolors.magenta} begins----------------------\n{bcolors.grey}"
                + json.dumps(json.load(f), indent=1)
                + f"{bcolors.magenta}\n----------------------sig {bcolors.blue}{sig}{bcolors.magenta} ends----------------------{bcolors.nc}")


def main():
    txs = sys.argv[1:]  # check command line args
    if txs == []:
        print(
            f"{bcolors.red}error: no txs provided {bcolors.nc}(select transactions like 'python3 multisigner 0 1' for transactions 0 and 1)")
        exit()

    try:
        f = open(os.path.join(__location__, ".config.toml"))  # load user config
        config = toml.loads(f.read())
        settings = config["settings"]
    except FileNotFoundError:
        print(
            f"{bcolors.red}error{bcolors.nc}: config file not found.\n\n"
            f"quick setup:\n\n  1. {bcolors.blue}cp ./multisigner/config.toml ./multisigner/.config.toml{bcolors.nc}\n"
            f"  2. {bcolors.blue}nano multisigner/.config.toml{bcolors.nc} and fill in your info\n  3. run this program again\n")
        exit()

    try:
        NAME = (
            subprocess.check_output(["git", "config", "user.name"])  # check user's git username
            .decode("utf-8")
            .strip()
        )
        if not os.path.exists(f"./{settings['REPO'].split('/')[1]}"):
            subprocess.check_output(
                    ["gh", "repo", "clone", "https://github.com/" + settings["REPO"], "--", "--quiet"])
        subprocess.check_output(
                ["git", "--git-dir", f"./{settings['REPO'].split('/')[1]}/.git",
                "--work-tree", f"./{settings['REPO'].split('/')[1]}", "pull", "--quiet"])
    except (subprocess.CalledProcessError, FileNotFoundError):  # if no username we will print the signatures later as they can't be pushed
        NAME = ""
    if settings["ACCOUNT"]:
        acct = settings["ACCOUNT"]  # get the account number from config or rpc call
    else:
        try:
            acct = json.loads(
                subprocess.check_output(
                    ["osmosisd", "q", "account", settings["KEY"], "--node", settings["RPC"], "--output", "json"]).decode("utf-8")
                )["account_number"]
        except subprocess.CalledProcessError:
            print(
                f"{bcolors.red}rpc error. please check your connection, try a different node, or wait and try again")
            exit()
    if NAME:
        FILE = f"-{NAME}-sig.json" 
    else:
        print("\ngit/gh not installed/logged in. txs will be printed, not uploaded")
        FILE = "-sig.json"

    signed = []
    for tx in txs:  # downloaded designated txs
        r = requests.get(
            f"https://raw.githubusercontent.com/{settings['REPO']}/main/transactions/unsigned/{tx}.json")
        with open(f"/tmp/{tx}.json", "w") as f:
            f.write(r.text)
        print(f"\nplease check tx {bcolors.blue}{tx}{bcolors.nc} before signing:\n")  # print the "messages" to console for review
        with open(f"/tmp/{tx}.json") as f:
            print(
                bcolors.yellow
                + json.dumps(json.load(f)["body"]["messages"], indent=1)
                + f"\n{bcolors.nc}")
        try:
            subprocess.check_output(  #  sign the txs
                    ["osmosisd", "tx", "sign", f"/tmp/{tx}.json", "--from", settings["KEY"],
                    "--multisig", settings["MULTISIG"], "--keyring-backend", settings["KEYRING"], "--account-number", acct, "--sequence", tx,
                    "--chain-id", settings["CHAIN"], "--offline", "--output-document", f"/tmp/{tx}{FILE}"])
            if os.path.isfile(f"/tmp/{tx}{FILE}"):
                signed.append(tx)
        except subprocess.CalledProcessError:
            print(
                f"sig {tx} {bcolors.red}failed{bcolors.nc}. please check the tx or your config")

    if signed != []:  # choose to print or upload, or skip if not logged in
        if NAME:
            choice = input(
                "signatures completed\n\n   1) upload signatures to repo\n   2) print signatures to console\n\nyour choice: ")
            while choice != "1" and choice != "2":
                time.sleep(0.1)
                choice = input(
                    "invalid input. please enter 1 to upload or 2 to print signatures: ")
        else:
            choice = "2"
    else:
        print(f"{bcolors.red}error{bcolors.nc}: no signatures found")
        exit()

    if choice == "1":  # add signatures to repo and push to remote
        try:
            subprocess.check_output(
                    ["git", "--git-dir", f"./{settings['REPO'].split('/')[1]}/.git",
                    "--work-tree", f"./{settings['REPO'].split('/')[1]}", "pull", "--quiet"])
            for tx in signed:
                subprocess.check_output(
                        ["cp", f"/tmp/{tx}{FILE}",
                        f"./{settings['REPO'].split('/')[1]}/transactions/signatures/{tx}{FILE}"])
            subprocess.check_output(
                    ["git", "--git-dir", f"./{settings['REPO'].split('/')[1]}/.git",
                    "--work-tree", f"./{settings['REPO'].split('/')[1]}", "add", "./transactions/signatures/*"])
            subprocess.check_output(
                    [ "git", "--git-dir", f"./{settings['REPO'].split('/')[1]}/.git", "--work-tree",
                    f"./{settings['REPO'].split('/')[1]}", "commit", "-m" f"{NAME} signed {' '.join(signed)}"])
            subprocess.check_output(
                    ["git", "--git-dir", f"./{settings['REPO'].split('/')[1]}/.git",
                    "--work-tree", f"./{settings['REPO'].split('/')[1]}", "push", "--quiet"])
            print(f"\n{bcolors.green}signatures uploaded to repo{bcolors.nc}")
        except subprocess.CalledProcessError:
            print(
                f"{bcolors.red}error uploading signatures to repo{bcolors.nc}\n\nprinting now...")
            print_sig(signed, FILE)
    elif choice == "2":
        print_sig(signed, FILE)
    else:
        print("fatal error")
        exit()

if __name__ == "__main__":
    main()
