from flask import Flask, request, render_template_string, abort
import datetime
import html
import json

app = Flask(__name__)

LOG_FILE = "visitors.log"
SECRET_PASSWORD = "MySecretViewKey123"  # Change this before deploying.

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Scam Link Safety Check</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root {
            --mobitel-blue: #005eb8;
            --mobitel-green: #70bf44;
            --ink: #172033;
            --muted: #607085;
            --line: #dce5ef;
            --panel: #ffffff;
            --warning: #f7b731;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, Helvetica, sans-serif;
            color: var(--ink);
            background:
                linear-gradient(135deg, rgba(0, 94, 184, .14), rgba(112, 191, 68, .14)),
                #f6f9fc;
        }
        .shell {
            width: min(940px, calc(100% - 32px));
            margin: 0 auto;
            padding: 28px 0 40px;
        }
        .brandbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
            padding: 16px 0 22px;
            border-bottom: 4px solid var(--mobitel-green);
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 800;
            color: var(--mobitel-blue);
        }
        .mark {
            display: grid;
            place-items: center;
            width: 44px;
            height: 44px;
            border-radius: 8px;
            background: linear-gradient(145deg, var(--mobitel-blue), #0086d6);
            color: white;
            border-bottom: 5px solid var(--mobitel-green);
        }
        .tag {
            padding: 8px 12px;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: white;
            color: var(--muted);
            font-size: 13px;
            white-space: nowrap;
        }
        .hero {
            display: grid;
            grid-template-columns: minmax(0, 1.15fr) minmax(260px, .85fr);
            gap: 28px;
            align-items: stretch;
            padding-top: 34px;
        }
        .main, .side {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 14px 40px rgba(25, 53, 83, .10);
        }
        .main { padding: 34px; }
        h1 {
            margin: 0 0 14px;
            font-size: clamp(30px, 5vw, 56px);
            line-height: 1;
            color: var(--mobitel-blue);
        }
        p { line-height: 1.6; }
        .lead {
            margin: 0 0 24px;
            max-width: 620px;
            color: var(--muted);
            font-size: 17px;
        }
        .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }
        button {
            border: 0;
            border-radius: 6px;
            padding: 13px 20px;
            background: var(--mobitel-blue);
            color: white;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
        }
        button.secondary {
            color: var(--mobitel-blue);
            background: #e8f2fb;
        }
        .status {
            min-height: 24px;
            margin-top: 18px;
            color: var(--mobitel-blue);
            font-weight: 700;
        }
        .notice {
            margin-top: 26px;
            padding: 12px 14px;
            border-left: 4px solid var(--warning);
            background: #fff8e6;
            color: #735100;
            font-size: 13px;
            text-align: left;
        }
        .side { padding: 24px; }
        .meter {
            height: 12px;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--mobitel-green), var(--warning), #e74c3c);
            margin: 16px 0 24px;
        }
        .checklist {
            display: grid;
            gap: 12px;
            margin: 0;
            padding: 0;
            list-style: none;
        }
        .checklist li {
            padding: 12px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #fbfdff;
            color: var(--muted);
            font-size: 14px;
        }
        @media (max-width: 760px) {
            .brandbar {
                align-items: flex-start;
                flex-direction: column;
            }
            .hero { grid-template-columns: 1fr; }
            .main { padding: 26px; }
            .tag { white-space: normal; }
        }
    </style>
</head>
<body>
    <div class="shell">
        <header class="brandbar">
            <div class="brand">
                <div class="mark">SL</div>
                <div>
                    <div>Scam Link Trace</div>
                    <small>Mobitel-style safety awareness demo</small>
                </div>
            </div>
            <div class="tag">Independent anti-scam training page</div>
        </header>

        <main class="hero">
            <section class="main">
                <h1>Pause before you tap.</h1>
                <p class="lead">This link checker records basic diagnostic details so suspicious links can be reviewed by the site owner. Do not enter passwords, OTPs, NIC numbers, or payment details on unknown pages.</p>
                <div class="actions">
                    <button onclick="runCheck()">Run Safety Check</button>
                    <button class="secondary" onclick="showTips()">View Red Flags</button>
                </div>
                <div id="status" class="status"></div>
            </section>
            <aside class="side">
                <strong>Risk scan</strong>
                <div class="meter"></div>
                <ul class="checklist" id="tips">
                    <li>Unexpected free data, prizes, or urgent account warnings are common bait.</li>
                    <li>Shortened URLs and misspelled domains deserve extra caution.</li>
                    <li>Real providers never need your OTP to award a promotion.</li>
                </ul>
            </aside>
        </main>
    </div>
    <script>
        async function sendDiagnostics(action) {
            const fp = {
                action,
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                languages: navigator.languages,
                screenWidth: screen.width,
                screenHeight: screen.height,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                colorDepth: screen.colorDepth,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                cookiesEnabled: navigator.cookieEnabled,
                doNotTrack: navigator.doNotTrack,
                online: navigator.onLine,
                timestamp: new Date().toISOString()
            };
            await fetch('/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(fp)
            });
        }

        async function runCheck() {
            const status = document.getElementById('status');
            status.innerText = 'Checking link details...';
            await sendDiagnostics('safety_check');
            status.innerText = 'Safety check logged. Treat unexpected offer links as suspicious.';
        }

        async function showTips() {
            await sendDiagnostics('view_tips');
            document.getElementById('status').innerText = 'Red flags shown. Close this page if it asked for secrets.';
        }
    </script>
</body>
</html>
"""


def get_real_ip():
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


def write_log(event_type, payload):
    entry = {
        "event": event_type,
        "ip": get_real_ip(),
        "method": request.method,
        "path": request.path,
        "query": request.query_string.decode("utf-8", errors="replace"),
        "headers": {
            "user_agent": request.headers.get("User-Agent"),
            "referer": request.headers.get("Referer"),
            "accept_language": request.headers.get("Accept-Language"),
            "accept": request.headers.get("Accept"),
            "host": request.headers.get("Host"),
            "origin": request.headers.get("Origin"),
            "x_forwarded_for": request.headers.get("X-Forwarded-For"),
            "x_forwarded_proto": request.headers.get("X-Forwarded-Proto"),
        },
        "payload": payload,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=True) + "\n")


@app.route("/")
def index():
    write_log("page_view", {"args": request.args.to_dict(flat=False)})
    return render_template_string(HTML_PAGE)


@app.route("/log", methods=["POST"])
def log_fingerprint():
    data = request.get_json(silent=True) or {}
    write_log("browser_diagnostics", data)
    return "ok"


@app.route("/geo", methods=["POST"])
def log_geo():
    data = request.get_json(silent=True) or {}
    write_log("location_submission", data)
    return "ok"


@app.route("/viewlog")
def view_log():
    password = request.args.get("key", "")
    if password != SECRET_PASSWORD:
        abort(403)
    if request.args.get("clear", "").lower() == "true":
        open(LOG_FILE, "w", encoding="utf-8").close()
        return "<pre>Log file cleared.</pre>"
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            contents = f.read()
    except FileNotFoundError:
        contents = "No visitors yet."
    return f"<pre>{html.escape(contents)}</pre>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
