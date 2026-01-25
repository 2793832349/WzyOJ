�#!/bin/bash

# 检查是否使用本地源码
if [ "$USE_LOCAL_SOURCE" = "true" ] && [ -d "/root/frontend-local" ]; then
    echo "Using local source from /root/frontend-local"
    cd /root/frontend-local
else
    echo "Using source from git clone"
    cd ./frontend
fi

yarn build
rm -rf /root/frontend-dist/*
cp -r ./dist/* /root/frontend-dist/
echo -e "\033[32mBUILD SUCCESS\033[0m"�*cascade08"(5ac4ce5149d5df03259d8e59c714ddf813d0c19c2,file:///root/deploy/config/build-frontend.sh:file:///root/deploy