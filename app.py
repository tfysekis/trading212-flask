from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
        return {"error": f"Failed to fetch {endpoint}", "details": str(e)}

@app.route('/proxy/portfolio', methods=['POST'])
def proxy_combined():
    print("✅ Received API call")

    try:
        # Force parsing the body as JSON
        data = request.get_json(force=True)
        print("📦 Raw data:", data)
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON format"}), 400

        api_key = data.get("apiKey")
        print("🔑 API key:", api_key)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "details": str(e)}), 400

    if not api_key:
        return jsonify({"error": "No API key provided"}), 400

    portfolio = run_curl(api_key, "/api/v0/equity/portfolio")
    account = run_curl(api_key, "/api/v0/equity/account/cash")

    return jsonify({
        "portfolio": portfolio if isinstance(portfolio, list) else [],
        "account": account if isinstance(account, dict) else {}
    })



@app.route('/proxy/orders', methods=['POST'])
def proxy_orders():
    api_key = request.json.get("apiKey")
    orders = run_curl(api_key, "/api/v0/equity/history/orders?cursor=0&limit=20")
    return jsonify(orders)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
