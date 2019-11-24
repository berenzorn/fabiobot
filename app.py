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
def message():
    try:
        return "\n".join(user_creds[request.args.get('text')])
    except KeyError:
        return Response(status=404)


if __name__ == '__main__':
    app.run()
