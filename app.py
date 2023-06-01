"""This is the main file of the project."""
from flask import Flask, request, Response

import utilities as utils

config = utils.read_config()

app = Flask(__name__)


@app.route('/alchemy', methods=['POST'])
def alchemy():
    print('test')
    print(request.json)
    return Response(status=200)


if __name__ == '__main__':
    app.run()
