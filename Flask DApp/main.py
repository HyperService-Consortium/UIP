
from flask import (
    Flask,
    jsonify,
    make_response,
    request,
    abort
)

import requests

import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-p", "--port", type=int, default=21333, help="port of flask-dapp")

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello World"


intents = {
    'test': "testing",
    'test2': 1
}
HTTP_HEADER = {'Content-Type': 'application/json'}


@app.route('/opintents', methods=['GET'])
def get_op_intents():
    return jsonify({'intents': intents})


@app.route('/opintents', methods=['POST'])
def set_op_intents():
    return jsonify({'task': intents}), 201


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/post', methods=['POST'])
def post_op_intents():
    op_intents = request.get_json()
    print(type(op_intents), op_intents)
    # response = requests.post(
    #     url=host_to_send,
    #     headers=HTTP_HEADER,
    #     data=op_intents
    # )
    return jsonify({'intents': op_intents})


if __name__ == '__main__':
    console_args = vars(arg_parser.parse_args())
    app.run("127.0.0.1", port=console_args['port'])
