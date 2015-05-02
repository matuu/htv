# encoding=utf-8
import twitter
from os import path
from json import dumps
from bottle import Bottle, request, abort, static_file, view
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

from config.settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET

ROOT = path.abspath(".")

app = Bottle()


@app.route('/')
@view('index')
def index():
    return dict()


@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=ROOT + '/static')


@app.route('/update')
def update():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, "Expected WebSocket request.")

    api = twitter.Api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    # print api.VerifyCredentials()
    last_id = 1
    last_query = ""
    while True:
        try:
            query = wsock.receive()
            print "recibido", query
            # Si cambia la búsqueda, reseteo el valor de last_id,
            # así no dejo tweets afuera.
            if last_query != query:
                last_id = 1
            tweets = api.GetSearch(query, result_type='recent', since_id=last_id, count=5)
            last_query = query
            if tweets:
                last_id = tweets[0].GetId()
                wsock.send(dumps([x.AsJsonString() for x in tweets]))
            else:
                wsock.send("0 tweets")
        except WebSocketError:
            wsock.send("Conexión abortada")


if __name__ == '__main__':
    server = WSGIServer(("0.0.0.0", 8080), app, handler_class=WebSocketHandler)
    server.serve_forever()
