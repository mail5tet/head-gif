
from flask import Flask, request, make_response, jsonify, Response, send_from_directory
import base64
import datetime
import requests
import csv
import os

app = Flask(__name__, static_folder='.')

# 1x1 transparent PNG in base64
PIXEL_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAEklEQVR4nGNgYGBgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
)

LOG_FILE = "pixel_log.csv"
USERNAME = "admin"
PASSWORD = "supersecret"

# Ensure log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "ip", "uid", "user_agent", "city", "region", "country"])

def get_geo_info(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        if response.status_code == 200:
            data = response.json()
            return data.get("city", ""), data.get("region", ""), data.get("country", "")
    except Exception as e:
        print(f"Geo lookup failed: {e}")
    return "", "", ""

@app.route('/images/q4stats.gif')
def tracking_pixel():
    uid = request.args.get("uid", "unknown")
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "unknown")
    timestamp = datetime.datetime.utcnow().isoformat()

    city, region, country = get_geo_info(ip)

    with open(LOG_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, uid, user_agent, city, region, country])

    pixel_data = base64.b64decode(PIXEL_BASE64)
    response = make_response(pixel_data)
    response.headers.set("Content-Type", "image/gif")
    response.headers.set("Content-Length", len(pixel_data))
    return response

def check_auth(auth_header):
    if not auth_header:
        return False
    try:
        auth_type, credentials = auth_header.split()
        if auth_type.lower() != 'basic':
            return False
        decoded = base64.b64decode(credentials).decode('utf-8')
        username, password = decoded.split(':')
        return username == USERNAME and password == PASSWORD
    except:
        return False

@app.route('/logs')
def view_logs():
    auth_header = request.headers.get('Authorization')
    if not check_auth(auth_header):
        return Response(
            'Authentication required', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline='') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            for row in reader:
                if len(row) == 7:
                    logs.append({
                        "timestamp": row[0],
                        "ip": row[1],
                        "uid": row[2],
                        "user_agent": row[3],
                        "city": row[4],
                        "region": row[5],
                        "country": row[6],
                    })
    return jsonify(logs)

@app.route('/redirect')
def serve_redirect():
    return send_from_directory('.', 'redirect.html')

if __name__ == '__main__':
    app.run(debug=True)
