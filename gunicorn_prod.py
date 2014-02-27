import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1

'''
Point to local apache 
'''
bind = "127.0.0.1:8184"
#bind = "10.35.1.56:8183"

#daemon = True

pidfile = '/logs/icommons_ext_tools/gunicorn.pid'

accesslog = '/logs/icommons_ext_tools/gunicorn_access.log'

errorlog = '/logs/icommons_ext_tools/gunicorn_error.log'
