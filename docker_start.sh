#!/bin/sh

# Start redis
# redis-server --daemonize yes

# Start worker
# nohup python3 worker.py > worker.log &

# Start Server
uvicorn main:app --host 0.0.0.0 --port 8080 --log-level debug --reload