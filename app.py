
from flask import Flask, request, make_response, jsonify, Response, send_from_directory
import base64
import datetime
import requests
import csv
import os
import sys
import json

app = Flask(__name__, static_folder='.')

def log(message):
    print(f"[LOG] {message}", file=sys.stderr)

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
            writer.writerow(["timestamp", "ip", "uid", "user_agent", "city", "region", "country", "vpn", "proxy", "tor", "hosting"])
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

def is_vpn_ip(ip):
    try:
        api_key = os.getenv("IPQS_KEY", "YOUR_IPQS_KEY_HERE")
        url = f"https://ipqualityscore.com/api/json/ip/{api_key}/{ip}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get("vpn", False), data.get("proxy", False), data.get("tor", False), data.get("hosting", False)
        else:
            log(f"VPN check failed: HTTP {response.status_code}")
    except Exception as e:
        log(f"VPN check error: {e}")
    return False, False, False, False

@app.route('/images/q4stats.gif')
def tracking_pixel():
    uid = request.args.get("uid", "unknown")
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip = extract_real_ip(forwarded_for, request.remote_addr)
    user_agent = request.headers.get("User-Agent", "unknown")
    timestamp = datetime.datetime.utcnow().isoformat()

    log(f"Pixel requested | UID: {uid} | IP: {ip}")

    city, region, country = get_geo_info(ip)
    vpn, proxy, tor, hosting = is_vpn_ip(ip)

    try:
        with open(LOG_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, ip, uid, user_agent, city, region, country, vpn, proxy, tor, hosting])
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
                if len(row) == 11:
                    logs.append({
                        "timestamp": row[0],
                        "ip": row[1],
                        "uid": row[2],
                        "user_agent": row[3],
                        "city": row[4],
                        "region": row[5],
                        "country": row[6],
                        "vpn": row[7],
                        "proxy": row[8],
                        "tor": row[9],
                        "hosting": row[10],
                    })
    except Exception as e:
        log(f"Reading logs failed: {e}")

    log_lines = [json.dumps(entry) for entry in logs]
    return Response("\n".join(log_lines), mimetype="application/json")

    @app.route('/giphy_carol-burnett-maid-over-it-3ohzdUuqOMFwxPyUvu664783anp2NDd2em42MXVweml2dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw3ohzdUuqOMFwxPyUvu76-gif')
def redirect():
    return send_from_directory('.', 'redirect.html')

    @app.route('/giphy_SkyTV-homer-simpson-simpsons-hiding-2A3DG83664783anp2NDd2em42MXVwjfh6784GHGFjkfdkfheml2dCZlcD12MV9pbnRlcm5hbF9yvN8uaBiaNR-gif')
def redirect2():
    return send_from_directory('.', 'redirect2.html')

    @app.route('/pudgypenguins-fire-burning-on-ZhS9PL4HQO6o9s9G83664783anp2NDd2em42MXVwe64783anhjfHlksdjf5682dFG099jjjhrGGF647893456GFGgghjp2NDd2e6ce-gif')
def redirect3():
    return send_from_directory('.', 'redirect3.html')

    @app.route('/star-wars-han-solo-rHR8qPw3ohzdUuqUvu664783anpOMFwx1mC5m42MXVweml8377759fhhpoebfghjk8906GHghSqzjbcn543GHdkbxbHG2dCZlcD1O6o9s9G836V3G-gif')
def redirect4():
    return send_from_directory('.', 'redirect4.html')


if __name__ == '__main__':
    app.run(debug=True)
