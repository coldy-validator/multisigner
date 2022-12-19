#!/bin/bash

printf "enter "from" address: "
read -r key

function create_message {
case "$1" in "send"*)
tx=$(osmosisd tx bank $1 --from $key --generate-only)
;; "grant"*)
tx=$(osmosisd tx authz $1 --from $key --generate-only)
;; "vote"*)
tx=$(osmosisd tx gov $1 --from $key --generate-only)
;; *)
printf "error - tx not generated - check your inputs\n"
;; esac
if [ ! -z "$2" ] ; then
message=$(jq '.body.messages' <<<$tx)
tx=$(jq ".body.messages += $message" <<<$2)
fi
[ -z "$tx" ] && { printf "exiting\n" ; exit ; }
add_message "$tx"
}

function add_message {
  printf "add another message? [y/n]: "
  read -r choice
  while [ "$choice" != "y" ] && [ "$choice" != "n" ] ; do
    printf "error - choose "y" or "n": "
    read -r choice
  done
  if [ "$choice" == "y" ] ; then
    printf "enter your next message: "
    read -r n_message
    create_message "$n_message" "$1"
  else
    printf "\nyour completed tx:\n\n"
    jq . <<<$1
  fi
}

printf "enter the first tx message in an abreviated manner like such:\n\nsend tx:\nsend <from> <to> <amount>\nfor a vote tx:\nvote 69 yes\n\nsupported messages:\nsend, vote, \n\nyour message: "
read -r u_message
if [ ! -z "$u_message" ] ; then
  create_message "$u_message"
# printf "\nenter a sequence number or tx name to save to file: "
# read -r file
# cat $tx > $file
else
  printf "error - no input\n"
fi
