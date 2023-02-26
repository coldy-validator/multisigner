#!/usr/bin/env python
from os import path
from sys import argv
from time import sleep
from json import dumps,load,loads
from config import client,multisig
from __init__ import bcolors, __location__
from subprocess import check_output,CalledProcessError


def print_sig(signed):  # print signatures to console
    print(f"\nprinting signatures now. you can copy and paste this output")
    sleep(1)
    for sig in signed:
        with open(sig["file"]) as f:
            print(
                f"{bcolors.magenta}\n----------------------sig {bcolors.blue}{sig['tx']}{bcolors.magenta} begins----------------------\n{bcolors.grey}"
                + dumps(load(f), indent=1)
                + f"{bcolors.magenta}\n----------------------sig {bcolors.blue}{sig['tx']}{bcolors.magenta} ends----------------------{bcolors.nc}")

def main():
    try:
        check_output(["which", "osmosisd"])
    except CalledProcessError:
        print(f"{bcolors.red}error: osmosisd not installed.{bcolors.nc} please see <link> for a guide")
        exit()
    if not multisig["signer_address"] or not multisig["multisig_address"]:
        print(f"{bcolors.red}error: signer and/or multisig address not configured{bcolors.nc}")
        exit()
    txs = argv[1:]  # check command line args
    if txs == []:
        print(f"{bcolors.red}error: no txs provided {bcolors.nc}(select transactions like 'python3 multisigner 0 1' for transactions 0 and 1)")
        exit()
    try:
        if not client["binary"]:
            print(f"{bcolors.red}error: no binary name in config{bcolors.nc}")
            exit()
        else:
            binary = client["binary"]
    except FileNotFoundError:
        print(
            f"{bcolors.red}error{bcolors.nc}: config file not found.\n\n"
            f"quick setup:\n\n  1. {bcolors.blue}cp ./multisigner/config.py.sample ./multisigner/config.py{bcolors.nc}\n"
            f"  2. {bcolors.blue}nano multisigner/config.py{bcolors.nc} and fill in your info\n  3. run this program again\n")
        exit()
    try:
        name = (check_output(["git", "config", "user.name"]).decode("utf-8").strip())  # check user's git username
        if multisig["repo"]:
            repo = multisig["repo"]
            repo_dir = path.join(__location__, repo.split('/')[1])
            if not path.exists(repo_dir):  # if the repo exists in config, make sure we have it and pull changes
                check_output(
                    ["git", "clone", "git@github.com:" + repo, repo_dir, "--", "--quiet"])
            check_output(
                ["git", "--git-dir", f"{repo_dir}/.git",
                "--work-tree", repo_dir, "pull", "--quiet"])
        else:
            repo = "null"  # if no repo in config, we will print the signatures later as they can't be pushed
    except (CalledProcessError,FileNotFoundError):
        print(f"{bcolors.yellow}warn: git not configured{bcolors.nc}")
    if multisig["signer_name"]:
        name = multisig["signer_name"]
    else:
        name = "null"
    if not client["rpc"]:
        RPC = "null"
    else:
        RPC = client["rpc"]
    if multisig["account_number"]:
        acct = multisig["account_number"]  # get the account number from config or rpc call
    else:
        if RPC == "null":
            print("no rpc or account number in config. you need one or the other")
            exit()
        else:
            try:
                acct = loads(
                    check_output([binary, "q", "account", multisig["multisig_address"], "--node", RPC, "--output", "json"]).decode("utf-8"))["account_number"]
            except CalledProcessError:
                print(f"{bcolors.red}rpc error.{bcolors.nc} please check your connection, try a different node, or wait and try again - or add your account number to config for offline mode")
                exit()
    if name == "null":
        print("\ngit not installed/configured. txs will be printed, not uploaded")
    signed = []
    for tx in txs:  # fetch designated txs
        if tx.endswith("-local"):
            name = "null"  # if we get a local tx force print
            tx = tx.split("-")[0]
            tx_file = path.join(__location__, "local", "transactions", "unsigned", f"{tx}.json")
            sig_file = path.join(__location__, "local", "transactions", "signatures", f"{tx}-sig.json")
        else:
            if repo == "null":
                print("error - no repo in config and git signing attempted.")
                exit()
            tx_file = path.join(repo_dir, "transactions", "unsigned", f"{tx}.json")
            sig_file = path.join(repo_dir, "transactions", "signatures", f"{tx}-{name}-sig.json")
        if not path.exists(tx_file):
            print(f"error: {tx} - file not found")
            exit()
        print(f"\nplease check tx {bcolors.blue}{tx}{bcolors.nc} before signing:\n")  # print the "messages" to console for review
        with open(tx_file) as f:
            print(f"{bcolors.yellow}{dumps(load(f)['body']['messages'], indent=1)}\n{bcolors.nc}")
        if tx.isnumeric():  # if the tx name is numeric, we assume its the sequence number, if not we ask for one
            seq = tx
        else:
            seq = input("error - sequence number not provided. input sequence number if known, or 'n' to check rpc for next seq number: ")
            if seq == "n":
                if RPC == "null":
                    print("error - no rpc in config")
                else:
                    try:
                        seq = loads(check_output([binary, "q", "account", multisig["signer_address"], "--node", RPC, "--output", "json"]).decode("utf-8"))["sequence"]
                    except CalledProcessError:
                        print(f"{bcolors.red}rpc error. please check your connection, try a different node, or wait and try again - or enter sequence number")
            while not seq.isnumeric():
                seq = input("error - sequence number invalid. input sequence number if known: ")
        try:
            check_output(  #  sign the txs
                    [binary, "tx", "sign", tx_file, "--from", multisig["signer_address"],
                    "--multisig", multisig["multisig_address"], "--keyring-backend", client["keyring"], "--account-number", acct, "--sequence", seq,
                    "--chain-id", client["chain_id"], "--offline", "--output-document", sig_file])
            if path.isfile(sig_file):
                signed.append({"tx": tx, "file": sig_file})
        except CalledProcessError:
            print(f"sig {tx} {bcolors.red}failed{bcolors.nc}. please check the tx or your config")
    if signed != []:  # choose to print or upload, or skip if not logged in
        if name == "null" or repo == "null":
            choice = "2"
        else:
            choice = input("signatures completed\n\n   1) upload signatures to repo\n   2) print signatures to console\n\nyour choice: ")
            while choice != "1" and choice != "2":
                sleep(0.1)
                choice = input("invalid input. please enter 1 to upload or 2 to print signatures: ")
    else:
        print(f"{bcolors.red}error{bcolors.nc}: no signatures found")
        exit()
    if choice == "1":  # add signatures to repo and push to remote
        try:
            check_output(
                    ["git", "--git-dir", f"{repo_dir}/.git",
                    "--work-tree", repo_dir, "pull", "--quiet"])
            check_output(
                    ["git", "--git-dir", f"{repo_dir}/.git",
                    "--work-tree", repo_dir, "add", "./transactions/signatures/*"])
            check_output(
                    [ "git", "--git-dir", f"{repo_dir}/.git", "--work-tree",
                    repo_dir, "commit", "-m" f"{name} signed {' '.join([x['tx'] for x in signed])}"])
            check_output(
                    ["git", "--git-dir", f"{repo_dir}/.git",
                    "--work-tree", repo_dir, "push", "--quiet"])
            print(f"\n{bcolors.green}signatures uploaded to repo{bcolors.nc}")
        except CalledProcessError:
            print(f"{bcolors.red}error uploading signatures to repo{bcolors.nc}\n\nprinting now...")
            print_sig(signed)
    elif choice == "2":
        print_sig(signed)
    else:
        print("fatal error")
        exit()

if __name__ == "__main__":
    main()