import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1

bind = "127.0.0.1:8004"

'''
daemon = True

pidfile = 'gunicorn.pid'
'''
pythonpath = '/home/ubuntu/icommons_ext_tools'


accesslog = 'access.log'

errorlog = 'error.log'
