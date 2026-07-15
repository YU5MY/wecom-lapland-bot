@echo off
title 拉普兰德 Bot

echo [1/2] 启动服务端...
start /B "" "C:\Users\冯有生\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" main.py
echo 服务端已启动
timeout /t 3 /nobreak >nul

echo [2/2] 启动 Cloudflare 隧道...
echo 启动后请等待出现 trycloudflare.com 的地址
"D:\cloudflared\cloudflared.exe" tunnel --url http://localhost:80

echo.
pause
