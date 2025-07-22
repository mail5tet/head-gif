
from flask import Flask, request, make_response, jsonify, Response, send_from_directory
import base64
import datetime
import requests
import csv
import os
import sys

app = Flask(__name__, static_folder='.')

def log(message):
    print(f"[LOG] {message}", file=sys.stderr)

# Transparent pixel
PIXEL_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAEklEQVR4nGNgYGBgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
)

LOG_FILE = "pixel_log.csv"
USERNAME = "admin"
PASSWORD = "supersecret"

def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "ip", "uid", "user_agent", "city", "region", "country"])
        log("Initialized new log file")

init_log_file()

def extract_real_ip(x_forwarded_for, remote_addr):
    if x_forwarded_for:
        ip_list = [ip.strip() for ip in x_forwarded_for.split(',')]
        for ip in ip_list:
            if not ip.startswith("10.") and not ip.startswith("172.") and not ip.startswith("192.168"):
                return ip
    return remote_addr

def get_geo_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}"
        log(f"Requesting GeoIP info from: {url}")
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            log(f"GeoIP raw response: {data}")
            if data.get("status") == "success":
                city = data.get("city", "")
                region = data.get("regionName", "")
                country = data.get("country", "")
                return city, region, country
        else:
            log(f"GeoIP request failed: HTTP {response.status_code}")
    except Exception as e:
        log(f"Geo lookup failed: {e}")
    return "", "", ""

@app.route('/images/q4stats.gif')
def tracking_pixel():
    uid = request.args.get("uid", "unknown")
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip = extract_real_ip(forwarded_for, request.remote_addr)
    user_agent = request.headers.get("User-Agent", "unknown")
    timestamp = datetime.datetime.utcnow().isoformat()

    log(f"Pixel requested | UID: {uid} | IP: {ip}")

    city, region, country = get_geo_info(ip)

    try:
        with open(LOG_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, ip, uid, user_agent, city, region, country])
        log(f"Logged view for UID={uid}")
    except Exception as e:
        log(f"Failed to write log: {e}")

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
    except Exception as e:
        log(f"Auth error: {e}")
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
    try:
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
    except Exception as e:
        log(f"Reading logs failed: {e}")

    # Return each JSON object on a new line
    log_lines = [json.dumps(entry) for entry in logs]
    return Response("
".join(log_lines), mimetype="application/json")
    logs = []
    try:
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
    except Exception as e:
        log(f"Reading logs failed: {e}")
    return jsonify(logs)

@app.route('/redirect')
def serve_redirect():
    return send_from_directory('.', 'redirect.html')

if __name__ == '__main__':
    app.run(debug=True)
