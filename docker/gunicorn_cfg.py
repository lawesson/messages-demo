bind = "0.0.0.0:80"

worker_class = 'gthread'
workers = 4
threads = 5

max_requests = 100
max_requests_jitter = 2
timeout = 30
