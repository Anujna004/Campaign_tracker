from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
campaigns = db["campaigns"]


# Helper function to serialize MongoDB documents
def serialize_campaign(c):
    c["_id"] = str(c["_id"])
    return c 
@app.route("/hello")
def hello():
    return "Hello Flask!"


@app.route("/show-env")
def show_env():
    return f"MONGO_URI={os.getenv('MONGO_URI')}<br>DB_NAME={os.getenv('DB_NAME')}"


# -------------------- FRONTEND ROUTE --------------------
@app.route('/')
def index():
    return render_template('index.html')

# -------------------- LOGIN --------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if data.get("username") == "admin" and data.get("password") == "1234":
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# -------------------- ADD CAMPAIGN --------------------
@app.route("/api/campaigns", methods=["POST"])
def add_campaign():
    data = request.json
    required = ["name", "client", "startDate"]
    if not all(field in data and data[field] for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    new_campaign = {
        "name": data["name"],
        "client": data["client"],
        "startDate": data["startDate"],
        "status": data.get("status", "Active")
    }

    result = campaigns.insert_one(new_campaign)
    added = campaigns.find_one({"_id": result.inserted_id})
    return jsonify(serialize_campaign(added)), 201

# -------------------- GET CAMPAIGNS --------------------
@app.route("/api/campaigns", methods=["GET"])
def get_campaigns():
    q = request.args.get("q", "")
    query = {"$or": [
        {"name": {"$regex": q, "$options": "i"}},
        {"client": {"$regex": q, "$options": "i"}}
    ]} if q else {}

    data = [serialize_campaign(c) for c in campaigns.find(query).sort("_id", -1)]
    return jsonify(data)

# -------------------- UPDATE CAMPAIGN STATUS --------------------
@app.route("/api/campaigns/<id>/status", methods=["PATCH"])
def update_status(id):
    status = request.json.get("status")
    if status not in ["Active", "Paused", "Completed"]:
        return jsonify({"error": "Invalid status"}), 400

    result = campaigns.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    if result.matched_count == 0:
        return jsonify({"error": "Campaign not found"}), 404

    updated = campaigns.find_one({"_id": ObjectId(id)})
    return jsonify(serialize_campaign(updated)), 200

# -------------------- DELETE CAMPAIGN --------------------
@app.route("/api/campaigns/<id>", methods=["DELETE"])
def delete_campaign(id):
    result = campaigns.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify({"message": "Deleted successfully", "id": id})

# -------------------- DASHBOARD SUMMARY --------------------
@app.route("/api/summary", methods=["GET"])
def summary():
    total = campaigns.count_documents({})
    active = campaigns.count_documents({"status": "Active"})
    paused = campaigns.count_documents({"status": "Paused"})
    completed = campaigns.count_documents({"status": "Completed"})

    return jsonify({
        "total": total,
        "active": active,
        "paused": paused,
        "completed": completed
    })
# ✅ Test MongoDB connection route
@app.route("/test-db")
def test_db():
    try:
        db.list_collection_names()  # Try listing collections
        return f"✅ Connected to MongoDB: {db.name}"
    except Exception as e:
        return f"❌ Database connection error: {str(e)}"

# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

