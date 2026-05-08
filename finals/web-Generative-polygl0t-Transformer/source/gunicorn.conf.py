bind = "0.0.0.0:8000"
workers = 2
worker_class = "gthread"
threads = 4
timeout = 120
graceful_timeout = 30
keepalive = 5
preload_app = True
