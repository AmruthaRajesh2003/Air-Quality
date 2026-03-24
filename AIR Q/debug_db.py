from pymongo import MongoClient
import pandas as pd

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    db = client["air_quality_db"]
    col = db["readings"]
    docs = list(col.find().sort("timestamp", -1).limit(5))
    for doc in docs:
        print(doc)
except Exception as e:
    print("Error:", e)
