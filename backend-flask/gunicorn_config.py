import multiprocessing

# Bind to port from environment variable
bind = "0.0.0.0:5001"

# Number of workers (2 * CPU cores + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Timeout for workers
timeout = 120

# Log level
loglevel = "info"

# Access log file
accesslog = "-"

# Error log file
errorlog = "-"