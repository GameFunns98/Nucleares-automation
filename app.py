import os
import requests
from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Lock
from collections import deque

SERVER_URL = os.environ.get('NUCLEARES_SERVER_URL', 'http://localhost:8080')
# List of variables to track initially
TRACKED_VARS = [
    'TIME',
    'CORE_TEMP',
    'CORE_PRESSURE',
    'RODS_POS_ACTUAL',
    'CORE_STATE',
    'POWER_FROM_TURBINE_KW',
    'POWER_DEMAND_MW',
    'TIME_DAY',
]

app = Flask(__name__)

# Data store for graph history
data_lock = Lock()
history = {var: deque(maxlen=300) for var in TRACKED_VARS}
current_data = {var: 'N/A' for var in TRACKED_VARS}

# Alarm thresholds (placeholder values)
ALARM_THRESHOLDS = {
    'CORE_TEMP': 500,  # example threshold in degrees
    'CORE_PRESSURE': 220,  # example threshold in bar
}

alarms = []


def fetch_variable(name):
    try:
        resp = requests.get(f"{SERVER_URL}/?variable={name}")
        resp.raise_for_status()
        return resp.text.strip()
    except Exception as exc:
        return f"error: {exc}"


def update_data():
    global alarms
    new_alarms = []
    for var in TRACKED_VARS:
        value = fetch_variable(var)
        with data_lock:
            history[var].append({'value': value})
            current_data[var] = value
        # simple alarm check
        if var in ALARM_THRESHOLDS:
            try:
                numeric = float(value)
                if numeric >= ALARM_THRESHOLDS[var]:
                    new_alarms.append(f"{var} above threshold: {numeric}")
            except ValueError:
                pass
    alarms = new_alarms


scheduler = BackgroundScheduler()
scheduler.add_job(update_data, 'interval', seconds=5)
scheduler.start()
update_data()


@app.route('/')
def dashboard():
    with data_lock:
        current = {var: history[var][-1]['value'] if history[var] else 'N/A' for var in TRACKED_VARS}
    return render_template('dashboard.html', data=current, alarms=alarms)


@app.route('/history')
def history_json():
    with data_lock:
        return jsonify({var: list(history[var]) for var in TRACKED_VARS})


@app.route('/data')
def data_json():
    with data_lock:
        return jsonify({'current': current_data, 'alarms': alarms})


@app.route('/command', methods=['POST'])
def send_command():
    var = request.form.get('variable')
    value = request.form.get('value', '1')
    if not var:
        return jsonify({'status': 'error', 'message': 'variable required'}), 400
    try:
        resp = requests.post(f"{SERVER_URL}/?variable={var}&value={value}")
        resp.raise_for_status()
        return jsonify({'status': 'ok'})
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
