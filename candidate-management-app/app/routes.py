from flask import Blueprint, request, jsonify

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Candidate Management API is running!"})

@main.route('/submit_candidate', methods=['POST'])
def submit_candidate():
    data = request.json
    # For now, just return the submitted data as confirmation
    return jsonify({"status": "success", "submitted_data": data})
