import os
import random
import string
import json
from os.path import join, dirname, realpath
import pathlib
from dns import name
from flask import send_from_directory
import math
import pathlib
from flask import request
from flask import jsonify
from bson.json_util import dumps
from pymongo.srv_resolver import maybe_decode
from factory import create_app
from ml import prediction
from ml import read_txt_file
import random


app = create_app()


# link database
from flask_pymongo import PyMongo
mongo = PyMongo(app)
claimsCollections = mongo.db.Claims


def getNextId(collectionName):
    # generate a self-incremented claim id
    counters = mongo.db.Counter
    current = counters.find_one({"collection": collectionName})
    count = current['count'] + 1
    counters.update_one({'_id': current['_id']}, {"$set":{'count': count}})
    return count


# get ALL claims
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

# get ALL patients
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


# delete claims based on claimId
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


# delete patients based on name
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


# upload claims
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
    # riskLevel = int(prediction(read_txt_file(filePath)))
    riskLevel = random.randint(0,3)

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


# get report
@app.route('/report', methods=['GET'])
def getReport():
    
    queryClaimId = request.args.get('claimId')
    myquery = { "claimId": int(queryClaimId)}
    mydoc = claimsCollections.find_one(myquery)
    mydoc = json.loads(dumps(mydoc))
  

    if mydoc["riskLevel"] == '0':
        risk = "unlikely"
    elif mydoc["riskLevel"] == '1':
        risk = "low"
    elif mydoc["riskLevel"] == '2':
        risk = "mid"
    else:
        risk = "high"

    features = []
    fileExist = os.path.exists(mydoc["filePath"])
    if fileExist:
        with open(mydoc["filePath"],'r') as f:
            content = [item.strip() for item in f.readlines()]
            for line in content:
                parts = line.split('\t')
                features.append(parts)

    res = {
        "reportId": mydoc["claimId"],
        "riskLevel": risk,
        "patientName": mydoc["name"],
        "patientId": mydoc["patientId"],
        "reviewStatus": "Completed",        
        "claim": mydoc["filePath"],

        "providerName": features[0][6] if fileExist else "Null",
        "facilityLocation": features[0][7] if fileExist else "Null",
        "netValue":features[0][11] if fileExist else "Null",
        "billTimeDifference": features[0][5] if fileExist else "Null",
    }

    response = jsonify(res)
    return response, 200 


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)

