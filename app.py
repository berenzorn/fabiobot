from flask import Flask, request, Response
import private
import json

app = Flask(__name__)


@app.route('/addr')
def send_addr():
    try:
        return private.srv_address
    except AttributeError:
        return Response(status=404)


@app.route('/regex')
def send_regex():
    try:
        return private.regex
    except AttributeError:
        return Response(status=404)


@app.route('/token')
def send_token():
    try:
        return private.TOKEN
    except AttributeError:
        return Response(status=404)


@app.route('/proxy')
def send_proxy():
    try:
        return json.dumps(private.PROXY)
    except AttributeError:
        return Response(status=404)


@app.route('/check')
def check():
    try:
        _ = private.user_creds[request.args.get('text')]
        return Response(status=200)
    except KeyError:
        return Response(status=404)


@app.route('/msg')
def system():
    try:
        get_type = int(request.args.get('type'))
        name = private.user_creds[request.args.get('text')][2 * (get_type - 1)]
        passwd = private.user_creds[request.args.get('text')][2 * (get_type - 1) + 1]
        return f"{name} {passwd}"
    except KeyError:
        return Response(status=404)


@app.route('/all')
def whole():
    try:
        return "\n".join(private.user_creds[request.args.get('text')])
    except KeyError:
        return Response(status=404)


if __name__ == '__main__':
    app.run()
