import multiprocessing
import os

# Server socket
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')

# Worker processes
# A common formula is (2 * number of CPU cores) + 1
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'gthread')
threads = int(os.environ.get('GUNICORN_THREADS', '4'))

# Logging
loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr

# Process naming
proc_name = 'applaude_api'

# Timeouts
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', 90))

# Security: Set user and group if running as root
if os.geteuid() == 0:
    user = os.environ.get('GUNICORN_USER', 'applaude')
    group = os.environ.get('GUNICORN_GROUP', 'applaude')

# For running behind a proxy like NGINX or an AWS ELB
forwarded_allow_ips = '*'
