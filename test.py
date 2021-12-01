# import json

# from bson.json_util import dumps

# data = {
#             "_id": {
#                 "$oid": "619d77658ffe02fc0ee0ab0f"
#             },
#             "claimId": 9,
#             "comment": "",
#             "filePath": "/Users/xiaoyi/Postman/files/claim_test.txt",
#             "name": "Brittany Orn",
#             "patientId": 9,
#             "riskLevel": 3
# }

# mydoc = json.loads(dumps(data))

# with open(mydoc["filePath"],'r') as f:
#         content = [item.strip() for item in f.readlines()]
#         features = []
#         for line in content:
#             parts = line.split('\t')
#             features.append(parts)

# if mydoc["riskLevel"] == 0:
#     risk = "unlikely"
# elif mydoc["riskLevel"] == 1:
#     risk = "low"
# elif mydoc["riskLevel"] == 2:
#     risk = "mid"
# else:
#     risk = "high"

# table = {
#         "reportId": mydoc["claimId"],
#         "riskLevel": risk,
#         "patientName": mydoc["name"],
#         "patientId": mydoc["patientId"],
#         "reviewStatus": "Completed",        
#         "claim": mydoc["filePath"],

#         "providerName": features[0][6],
#         "facilityLocation": features[0][7],
#         "netValue":features[0][11],
#         "billTimeDifference": features[0][5],
# }

# print(table)
