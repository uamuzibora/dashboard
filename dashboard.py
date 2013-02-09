import sys
if sys.version_info>(2,6):
    from urlparse import parse_qs
else:
    from cgi import parse_qs
import wsgiref.util
import json
import get_data
import datetime

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
    req_type=param.get('request_type',[''])[0]
    if req_type=="dashboard":
        ret=get_data.dashboard(param.get('data',[''])[0])
    elif req_type=="report":
        start=param.get('start',[''])[0]
        start=datetime.datetime.strptime(start,"%d/%m/%Y")
        end=param.get('end',[''])[0]
        end=datetime.datetime.strptime(end,"%d/%m/%Y")
        location=param.get('location',[''])[0]
        ret=get_data.report(start,end,location)

    return json.dumps(ret)



if __name__=='__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(application,bindAddress = '/tmp/fcgi2.sock').run()
