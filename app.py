from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "my-secret-212-token")  # set this securely on Render

def run_curl(api_key, endpoint):
    curl_command = [
        "curl", "-s", "-X", "GET",
        f"https://live.trading212.com{endpoint}",
        "-H", f"Authorization: {api_key}"
    ]
    try:
        result = subprocess.check_output(curl_command, stderr=subprocess.STDOUT)
        return json.loads(result)
    except Exception as e:
        return {"error": str(e)}

@app.route('/proxy/portfolio', methods=['POST'])
def proxy_combined():
    data = request.get_json(force=True)
    token = data.get("token")
    api_key = data.get("apiKey")

    if token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403

    if not api_key:
        return jsonify({"error": "No API key provided"}), 400

    portfolio = run_curl(api_key, "/api/v0/equity/portfolio")
    account = run_curl(api_key, "/api/v0/equity/account/cash")

    return jsonify({
        "portfolio": portfolio if isinstance(portfolio, list) else [],
        "account": account if isinstance(account, dict) else {}
    })
