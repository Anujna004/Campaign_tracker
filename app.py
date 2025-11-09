from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# -------------------- LOAD ENVIRONMENT VARIABLES --------------------
# Loads .env locally; on Render, environment variables are read automatically
load_dotenv()

app = Flask(__name__)
CORS(app)

# -------------------- MONGODB CONNECTION --------------------
# TLS options ensure Atlas connection works correctly
client = MongoClient(
    os.getenv("MONGO_URI"),
    tls=True,
    tlsAllowInvalidCertificates=True
)
db = client[os.getenv("DB_NAME")]
campaigns = db["campaigns"]  # collection name

# -------------------- HELPER FUNCTIONS --------------------
def serialize_campaign(campaign):
    """Convert ObjectId to string for JSON serialization"""
    campaign["_id"] = str(campaign["_id"])
    return campaign

# -------------------- TEST ROUTES --------------------
@app.route("/hello")
def hello():
    return "Hello Flask!"

@app.route("/test-db")
def test_db():
    """Test MongoDB connection and list collections"""
    try:
        collections = db.list_collection_names()
        return f"✅ Connected to MongoDB: {db.name}, Collections: {collections}"
    except Exception as e:
        return f"❌ Database connection error: {str(e)}"

@app.route("/show-env")
def show_env():
    """Display environment variables (for testing only)"""
    return f"MONGO_URI={os.getenv('MONGO_URI')}<br>DB_NAME={os.getenv('DB_NAME')}"

# -------------------- FRONTEND ROUTE --------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------- LOGIN --------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "1234":
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# -------------------- CAMPAIGN ROUTES --------------------
@app.route("/api/campaigns", methods=["POST"])
def add_campaign():
    data = request.json
    required_fields = ["name", "client", "startDate"]

    # Validate required fields
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    new_campaign = {
        "name": data["name"],
        "client": data["client"],
        "startDate": data["startDate"],
        "status": data.get("status", "Active")  # default status
    }

    result = campaigns.insert_one(new_campaign)
    added = campaigns.find_one({"_id": result.inserted_id})
    return jsonify(serialize_campaign(added)), 201

@app.route("/api/campaigns", methods=["GET"])
def get_campaigns():
    """Get all campaigns or search by query (name or client)"""
    query_str = request.args.get("q", "")
    query = {
        "$or": [
            {"name": {"$regex": query_str, "$options": "i"}},
            {"client": {"$regex": query_str, "$options": "i"}}
        ]
    } if query_str else {}

    all_campaigns = [serialize_campaign(c) for c in campaigns.find(query).sort("_id", -1)]
    return jsonify(all_campaigns)

@app.route("/api/campaigns/<id>/status", methods=["PATCH"])
def update_status(id):
    """Update campaign status"""
    status = request.json.get("status")
    if status not in ["Active", "Paused", "Completed"]:
        return jsonify({"error": "Invalid status"}), 400

    result = campaigns.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    if result.matched_count == 0:
        return jsonify({"error": "Campaign not found"}), 404

    updated = campaigns.find_one({"_id": ObjectId(id)})
    return jsonify(serialize_campaign(updated)), 200

@app.route("/api/campaigns/<id>", methods=["DELETE"])
def delete_campaign(id):
    """Delete a campaign by ID"""
    result = campaigns.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify({"message": "Deleted successfully", "id": id})

# -------------------- DASHBOARD SUMMARY --------------------
@app.route("/api/summary", methods=["GET"])
def summary():
    """Return summary counts of campaigns by status"""
    return jsonify({
        "total": campaigns.count_documents({}),
        "active": campaigns.count_documents({"status": "Active"}),
        "paused": campaigns.count_documents({"status": "Paused"}),
        "completed": campaigns.count_documents({"status": "Completed"})
    })

# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Render requires host="0.0.0.0"
    app.run(host="0.0.0.0", port=port, debug=True)
