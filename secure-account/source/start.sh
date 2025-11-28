#!/bin/sh

echo -n "$A1CTF_FLAG" > /flag
unset A1CTF_FLAG
chmod a=,u=r /flag

pwdgen-daemon.py &

sleep 1s  # wait for server start.

# modify root password

password=$(pwdgen.py -l60)
echo "root:$password" | chpasswd 2> /dev/null

# add player user

adduser player -D
echo "player:player" | chpasswd 2> /dev/null

dropbear -RFEwgjk
