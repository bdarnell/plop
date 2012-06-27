#!/usr/bin/env python
import datetime
from plop.collector import Collector
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options
from tornado.web import Application, RequestHandler, asynchronous

define('port', default=8888)
define('output_file', default='profile.out')

class HelloHandler(RequestHandler):
    @asynchronous
    @gen.engine
    def get(self):
        # Completely unnecessary, it just brings in a little more code
        # to make for a more interesting profile.
        yield gen.Task(IOLoop.instance().add_callback)
        self.render("hello.html", name="world")

class ProfileHandler(RequestHandler):
    @asynchronous
    def get(self):
        self.collector = Collector()
        self.collector.start()
        IOLoop.instance().add_timeout(datetime.timedelta(seconds=60),
                                      self.finish_profile)

    def finish_profile(self):
        self.collector.stop()
        self.finish(repr(dict(self.collector.stack_counts)))

@gen.engine
def generate_traffic():
    client = AsyncHTTPClient()
    while True:
        resp = yield gen.Task(client.fetch,
                              'http://localhost:%d/' % options.port)
        assert resp.body.strip() == 'Hello world!'

def main():
    parse_command_line()

    app = Application([
            ('/', HelloHandler),
            ('/_profile', ProfileHandler),
            ], log_function=lambda x: None)
    app.listen(options.port, address='localhost')

    generate_traffic()
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
