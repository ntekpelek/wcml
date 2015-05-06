# -*- coding: utf-8 -*-

#  routers are dictionaries of URL routing parameters.
#
#  This simple router set overrides only the default application name,
#  but provides full rewrite functionality.

routers = dict(

    # base router
    BASE=dict(
        default_application='wcml_webapp',
    ),
)

# Specify log level for rewrite's debug logging
# Possible values: debug, info, warning, error, critical (loglevels),
#                  off, print (print uses print statement rather than logging)
# GAE users may want to use 'off' to suppress routine logging.
#
logging = 'off'

# Error-handling redirects all HTTP errors (status codes >= 400) to a specified
# path.  If you wish to use error-handling redirects, uncomment the tuple
# below.  You can customize responses by adding a tuple entry with the first
# value in 'appName/HTTPstatusCode' format. ( Only HTTP codes >= 400 are
# routed. ) and the value as a path to redirect the user to.  You may also use
# '*' as a wildcard.
#
# The error handling page is also passed the error code and ticket as
# variables.  Traceback information will be stored in the ticket.
#
# routes_onerror = [
#     (r'init/400', r'/init/default/login')
#    ,(r'init/*', r'/init/static/fail.html')
#    ,(r'*/404', r'/init/static/cantfind.html')
#    ,(r'*/*', r'/init/error/index')
# ]

# specify action in charge of error handling
#
# error_handler = dict(application='error',
#                      controller='default',
#                      function='index')

# In the event that the error-handling page itself returns an error, web2py will
# fall back to its old static responses.  You can customize them here.
# ErrorMessageTicket takes a string format dictionary containing (only) the
# "ticket" key.

# error_message = '<html><body><h1>%s</h1></body></html>'
# error_message_ticket = '<html><body><h1>Internal error</h1>Ticket issued: <a href="/admin/default/ticket/%(ticket)s" target="_blank">%(ticket)s</a></body></html>'


def __routes_doctest():
    '''
    Dummy function for doctesting routes.py.

    Use filter_url() to test incoming or outgoing routes;
    filter_err() for error redirection.

    filter_url() accepts overrides for method and remote host:
        filter_url(url, method='get', remote='0.0.0.0', out=False)

    filter_err() accepts overrides for application and ticket:
        filter_err(status, application='app', ticket='tkt')

    >>> import os
    >>> import gluon.main
    >>> from gluon.rewrite import load, filter_url, filter_err, get_effective_router
    >>> load(routes=os.path.basename(__file__))

    >>> filter_url('http://domain.com/abc', app=True)
    'welcome'
    >>> filter_url('http://domain.com/welcome', app=True)
    'welcome'
    >>> os.path.relpath(filter_url('http://domain.com/favicon.ico'))
    'applications/welcome/static/favicon.ico'
    >>> filter_url('http://domain.com/abc')
    '/welcome/default/abc'
    >>> filter_url('http://domain.com/index/abc')
    "/welcome/default/index ['abc']"
    >>> filter_url('http://domain.com/default/abc.css')
    '/welcome/default/abc.css'
    >>> filter_url('http://domain.com/default/index/abc')
    "/welcome/default/index ['abc']"
    >>> filter_url('http://domain.com/default/index/a bc')
    "/welcome/default/index ['a bc']"

    >>> filter_url('https://domain.com/app/ctr/fcn', out=True)
    '/app/ctr/fcn'
    >>> filter_url('https://domain.com/welcome/ctr/fcn', out=True)
    '/ctr/fcn'
    >>> filter_url('https://domain.com/welcome/default/fcn', out=True)
    '/fcn'
    >>> filter_url('https://domain.com/welcome/default/index', out=True)
    '/'
    >>> filter_url('https://domain.com/welcome/appadmin/index', out=True)
    '/appadmin'
    >>> filter_url('http://domain.com/welcome/default/fcn?query', out=True)
    '/fcn?query'
    >>> filter_url('http://domain.com/welcome/default/fcn#anchor', out=True)
    '/fcn#anchor'
    >>> filter_url('http://domain.com/welcome/default/fcn?query#anchor', out=True)
    '/fcn?query#anchor'

    >>> filter_err(200)
    200
    >>> filter_err(399)
    399
    >>> filter_err(400)
    400
    '''
    pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()
