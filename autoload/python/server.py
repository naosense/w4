#!/usr/bin/env python
# -.- coding: utf-8 -.-
import os
import sys
import json
import utils
import logic

if utils.is_py2:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import urlparse, unquote
elif utils.is_py3:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, unquote

HTTP_SERVER = None
# {timestamp:{timestamp:,who:,what:...}}
VIM_CONTENT_DICT = {}


class RequestHandler(BaseHTTPRequestHandler):

    def set_headers(self, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        params = urlparse(self.path)
        path = params.path
        query = params.query

        if path.endswith('index'):
            self.set_headers('text/html; charset=UTF-8')
            f = open(os.path.dirname(os.path.realpath(__file__)) + '/web/index.html', 'r')
            utils.write(self.wfile, f.read())
            f.close()
        elif path.endswith('.js'):
            self.set_headers('application/javascript; charset=UTF-8')
            f = open(os.path.dirname(os.path.realpath(__file__)) + '/web' + path, 'r')
            utils.write(self.wfile, f.read())
            f.close()
        elif path.endswith('.css'):
            self.set_headers('text/css; charset=UTF-8')
            f = open(os.path.dirname(os.path.realpath(__file__)) + '/web' + path, 'r')
            utils.write(self.wfile, f.read())
            f.close()
        elif path.endswith('.json'):
            self.set_headers('application/json; charset=UTF-8')
            response = {'code': 0}
            query_components = dict(qc.split("=") for qc in query.split("&"))
            kw = unquote(query_components['kw'])
            if kw.startswith('/figures'):
                response['data'] = utils.figure_relation_data(VIM_CONTENT_DICT)
            elif kw.startswith('/backtrack'):
                response['data'] = utils.event_relation_data(VIM_CONTENT_DICT)
            else:
                logic_expression = '' if kw.startswith('/all') else logic.Expression(
                    kw if kw.startswith('(') else '(' + kw + ')')
                # sort by line number
                sorted_dict = sorted(VIM_CONTENT_DICT.items(), key=lambda x: x[1]['ln'])
                data = []
                for source_timestamp, source_event in sorted_dict:
                    link_events = [VIM_CONTENT_DICT[target_timestamp] for target_timestamp in source_event['link']
                                   if target_timestamp != source_timestamp and target_timestamp in VIM_CONTENT_DICT]
                    link_html = '' if not link_events \
                        else ''.join([utils.event_to_tooltip_html(e) for e in link_events])
                    if logic_expression:
                        if logic_expression.predicate(source_event):
                            data.append(
                                '<tr id="' + str(source_event['ln']) + '"><td>'
                                + utils.join_when_where(source_event)
                                + '</td><td>'
                                + (''.join(source_event['who']) + ': ')
                                + source_event['what']
                                + link_html
                                + '</td></tr>'
                            )
                    else:
                        if kw.startswith('/all'):
                            data.append(
                                '<tr id="' + str(source_event['ln']) + '"><td>'
                                + utils.join_when_where(source_event)
                                + '</td><td>'
                                + (''.join(source_event['who']) + ': ')
                                + source_event['what']
                                + link_html
                                + '</td></tr>'
                            )
                response['data'] = data
            utils.write(self.wfile, json.dumps(response))
        elif path.endswith('stop'):
            import threading
            self.set_headers('application/json; charset=UTF-8')
            utils.write(self.wfile, json.dumps({'code': 0}))
            global HTTP_SERVER
            threading.Thread(target=HTTP_SERVER.shutdown, daemon=True).start()
        else:
            self.set_headers('application/json; charset=UTF-8')
            utils.write(self.wfile, json.dumps({'status': 'SUCCESS', 'path:': self.path}))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = utils.read(self.rfile, content_length)
        global VIM_CONTENT_DICT
        VIM_CONTENT_DICT = utils.vim_lines_dict(utils.vim_lines(post_data))
        self.set_headers('application/json; charset=UTF-8')
        utils.write(self.wfile, json.dumps({'code': 0}))


if __name__ == '__main__':
    HTTP_SERVER = HTTPServer(('localhost', int(sys.argv[1])), RequestHandler)
    HTTP_SERVER.serve_forever()
