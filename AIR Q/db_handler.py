from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "air_quality_db"
COLLECTION_NAME = "readings"

# Module-level singleton — no Streamlit dependency so this
# file can be safely imported by both app.py and api_server.py
_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    try:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        _client.server_info()  # Will raise if Mongo is not running
        _collection = _client[DB_NAME][COLLECTION_NAME]
        print(f"[DB] Connected to MongoDB: {DB_NAME}.{COLLECTION_NAME}")
        return _collection
    except Exception as e:
        print(f"[DB] MongoDB connection failed: {e}")
        return None

def save_reading(data: dict):
    """Save a sensor reading dict to MongoDB. Returns (success: bool, message: str)."""
    col = get_collection()
    if col is None:
        return False, "Database connection failed."
    data = dict(data)  # copy so we don't mutate the caller's dict
    data.setdefault("timestamp", datetime.now())
    try:
        col.insert_one(data)
        return True, "Reading saved successfully!"
    except Exception as e:
        return False, f"Error saving reading: {e}"

def get_history(limit: int = 20):
    """Return the last `limit` readings, newest first, as a list of dicts."""
    col = get_collection()
    if col is None:
        return []
    try:
        cursor = col.find().sort("timestamp", -1).limit(limit)
        return list(cursor)
    except Exception as e:
        print(f"[DB] Error fetching history: {e}")
        return []
