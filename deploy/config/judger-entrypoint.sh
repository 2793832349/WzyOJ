#!/bin/bash
rm -rf /judger/*
mkdir -p /judger/run /judger/spj

chown compiler:code /judger/run
chmod 711 /judger/run

chown compiler:spj /judger/spj
chmod 710 /judger/spj

echo "Dispatching the WS server."
export PYTHONDONTWRITEBYTECODE=1
exec python3 -B -u server.py
