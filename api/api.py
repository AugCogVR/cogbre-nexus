from flask import Flask, request, jsonify
from flask_restful import Resource, Api #, reqparse
#import pandas as pd
#import ast
import random
import string


app = Flask(__name__)
api = Api(app)

class FileStats(Resource):
    def post(self):
        content = request.get_json(force = True)
        print('POSTED: userId =', content['userId'])

        # data = pd.read_csv('users.csv')  # read CSV
        # data = data.to_dict()  # convert dataframe to dictionary
        data = {}
        data['whatever'] = 'stuff ' + (''.join(random.choice(string.ascii_lowercase) for i in range(10)))
        return data, 200  # return data and 200 OK code


api.add_resource(FileStats, '/filestats')  # entry point

if __name__ == '__main__':
    app.run()  # run our Flask app

