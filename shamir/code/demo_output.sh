#!/bin/bash

read  -n 1 -s
echo -n "Sending Update to Client Node" >/dev/tcp/localhost/55556

read  -n 1 -s
echo -n "Got share" >/dev/tcp/localhost/55556

read  -n 1 -s
echo -n "Node registered: web" >/dev/tcp/localhost/55556

read  -n 1 -s
echo -n "Node registered: face" >/dev/tcp/localhost/55556

read  -n 1 -s
echo -n "Node registered: qr" >/dev/tcp/localhost/55556

read  -n 1 -s
echo -n "Node registered: web" >/dev/tcp/localhost/55556

read  -n 1 -s
echo -n "Sending New Share to other Auth Nodes" >/dev/tcp/localhost/55556

read  -n 1 -s
echo -n "r3k has submitted 1 shares!" >/dev/tcp/localhost/55556

read  -n 1 -s
echo -n "tim has submitted 1 shares!" >/dev/tcp/localhost/55556

read  -n 1 -s
echo -n "r3k has submitted 1 shares!" >/dev/tcp/localhost/55556
read  -n 1 -s
echo -n "(r3k) is Authorized!" >/dev/tcp/localhost/55556
read  -n 1 -s
echo -n "r3k has submitted 1 shares!" >/dev/tcp/localhost/55556

exit 1
