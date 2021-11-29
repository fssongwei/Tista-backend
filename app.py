from flask import Flask
from flask import request
from flask import jsonify
from werkzeug.utils import secure_filename
import os
import random
import string
from os.path import join, dirname, realpath
import pathlib
from flask import send_from_directory
from ml import getRiskLevel
import math
from bson.json_util import dumps
import json
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = join(dirname(realpath(__file__)), './static/uploads/')

# app.run(debug=True)

# link database
from flask_pymongo import PyMongo
app.config["MONGO_URI"] = os.environ.get("MONGO_URL")
mongo = PyMongo(app)
claimsCollections = mongo.db.Claims


def getNextId(collectionName):
    # generate a self-incremented claim id
    counters = mongo.db.Counter
    current = counters.find_one({"collection": collectionName})
    count = current['count'] + 1
    counters.update_one({'_id': current['_id']}, {"$set":{'count': count}})
    return count


@app.route('/claims', methods=['GET'])
def getClaims():
    search = request.args.get('search')
    status = request.args.get('status')
    level = request.args.get('level')
    page = request.args.get('page') or 1
    pageSize = request.args.get('pageSize') or 10
    page = int(page)
    pageSize = int(pageSize)

    query = {}
    if search: query["name"] = search    
    totalCount = claimsCollections.count_documents(query)
    totalPage = math.ceil(totalCount / float(pageSize))
    data = claimsCollections.find(query).skip((page - 1) * pageSize).limit(pageSize)
    data = json.loads(dumps(data))

    pager = {
        "totalCount": totalCount,
        "totalPage": totalPage,
        "currentPage": page,
        "pageSize": pageSize
    }

    res = {
        "pagerData": pager,
        "tableData": data
    }

    response = jsonify(res)
    return response, 200

@app.route('/upload', methods=['POST'])
def upload():
    # save file
    claim = request.form
    if 'file' not in request.files:
        return jsonify(STATUS="ERROR", msg="Missing Claim File"), 500
    file = request.files['file']
    extension = pathlib.Path(file.filename).suffix
    filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15)) + extension;
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    filePath = "/static/uploads/" + filename;

    # run machine learning model
    riskLevel = getRiskLevel("." + filePath)

    # validate claim data
    name = claim["name"] or "John Doe"
    patientId = claim["patientId"] or getNextId("Patients")
    comment = claim["comment"]
    claimId = getNextId("Claims")

    # insert claim into database
    claimObjId = claimsCollections.insert({"name": name, "patientId": patientId, "comment": comment, "claimId": claimId, "filePath": filePath, "riskLevel": riskLevel});
    response = jsonify(
        STATUS="SUCCESS",
        claimId=claimId
    )
    return response, 200

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)