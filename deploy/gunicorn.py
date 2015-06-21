"""gunicorn WSGI server configuration."""
from multiprocessing import cpu_count

max_requests = 1000
worker_class = "sync"
workers = cpu_count() * 2
proc_name = 'workup'
loglevel = 'error'
logfile = '/path/to/error.log'
