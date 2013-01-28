import sys
if sys.version_info>(2,6):
    from urlparse import parse_qs
else:
    from cgi import parse_qs
import wsgiref.util
import json
import get_data

def application(environ, start_response):
    """
    Main application that get's called
    """
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]

    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    param = parse_qs(request_body);
    start_response(status, response_headers)
    if "data" in param.key():
        ret=get_data.get_data(param.get('data',[''])[0])
    else:
        ret="Need to specify which data to be requested"

    return json.dumps(ret)



if __name__=='__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(application,bindAddress = '/tmp/fcgi2.sock').run()
