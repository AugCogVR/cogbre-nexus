from flask import Flask, request #, jsonify
from flask_restful import Resource, Api #, reqparse
#import pandas as pd
#import ast
import random
import string
import json


app = Flask(__name__)
api = Api(app)

blocks = ''

class SyncPortal(Resource):
    def post(self):
        content = request.get_json(force = True)
        print('POSTED: userId =', content['userId'], 'command =', content['command'])

        stub = {}
        stub['whatever'] = 'stuff ' + (''.join(random.choice(string.ascii_lowercase) for i in range(10)))

        return stub, 200  # return data and 200 OK code


api.add_resource(SyncPortal, '/sync_portal')  # entry point


if __name__ == '__main__':

    blocks_file = open('../data/samples/elf_fib_recursive/basic_blocks')
    blocks = json.load(blocks_file)
    #print(blocks[0])
    # for i in blocks[0]['basic_blocks']:
    #     print(i)
    #     print(blocks[0]['basic_blocks'][i])

    blocks_file.close()

    app.run()  # run our Flask app

