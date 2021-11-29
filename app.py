import os
import random
import string
import json
import math
import pathlib
from flask import request
from flask import jsonify
from bson.json_util import dumps
from factory import create_app
from ml import prediction
from ml import read_txt_file



app = create_app()


# link database
from flask_pymongo import PyMongo
app.config["MONGO_URI"] = "mongodb+srv://tista:cornell2021@cluster0.9dx7j.mongodb.net/test?retryWrites=true&w=majority"
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
    if search: query["claimId"] = search    #claimId?? 
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

@app.route('/patients', methods=['GET'])
def getPatients():
    search = request.args.get('search')
    status = request.args.get('status')
    level = request.args.get('level')  
    page = request.args.get('page') or 1
    pageSize = request.args.get('pageSize') or 10
    page = int(page)
    pageSize = int(pageSize)

    query = {}
    if search: query["name"] = search     #name??
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


@app.route('/claims', methods=['DELETE'])
def deleteClaims():
    #delete claims
    claimId = request.args.get('claimId')
    myquery = { "claimId": claimId }
    claimsCollections.delete_one(myquery)
    
    response = jsonify(
        STATUS="SUCCESS",
    )
    return response, 200


@app.route('/patients', methods=['DELETE'])
def deletePatients():
    #delete patients
    patientName = request.args.get('patient')
    myquery = { "name": patientName }
    claimsCollections.delete_many(myquery)
    
    response = jsonify(
        STATUS="SUCCESS",
    )
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
    filePath = "./static/uploads/" + filename;


    # run machine learning model
    riskLevel = int(prediction(read_txt_file(filePath)))
    print(riskLevel)

    # validate claim data
    name = claim["name"] or "John Doe"
    patientId = claim["patientId"] or getNextId("Patients")
    comment = claim["comment"]
    claimId = '0'  #Hardcoding
    # claimId = getNextId("Claims")

    # insert claim into database
    claimObjId = claimsCollections.insert({"name": name, "patientId": patientId, "comment": comment, "claimId": claimId, "filePath": filePath, "riskLevel": riskLevel});
    
    response = jsonify(
        STATUS="SUCCESS",
        claimId=claimId
    )
    return response, 200
