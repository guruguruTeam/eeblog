# config.py
# -*- coding: UTF-8 -*-

bind="0.0.0.0:1234"
workers=4
daemon=True
backlog=2048
worker_connections=1000
pidfile="gunicorn.pid"
accesslog="access.log"
errorlog="gunicorn.log"