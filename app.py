from flask import Flask, request, Response
from private import user_creds

app = Flask(__name__)


@app.route('/check')
def check():
    try:
        _ = user_creds[request.args.get('text')]
        return Response(status=200)
    except KeyError:
        return Response(status=404)


@app.route('/msg')
def system():
    try:
        get_type = int(request.args.get('type'))
        name = user_creds[request.args.get('text')][2 * (get_type - 1)]
        passwd = user_creds[request.args.get('text')][2 * (get_type - 1) + 1]
        return f"{name} {passwd}"
    except KeyError:
        return Response(status=404)


@app.route('/all')
def whole():
    try:
        return "\n".join(user_creds[request.args.get('text')])
    except KeyError:
        return Response(status=404)


if __name__ == '__main__':
    app.run()
