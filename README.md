# Nucleares Automation Dashboard

This project provides a simple Flask-based dashboard for the game **Nucleares**. It connects to the in-game webserver to monitor reactor variables and display them in real time. A basic alarm system and graph are included as a starting point for further automation.

## Features

- Polls the game's webserver for selected variables.
- Displays current values and active alarms.
- Shows a line graph of core temperature.
- Placeholder thresholds for alarms and a framework for adding full automation.

## Requirements

- Python 3.8+
- Packages from `requirements.txt`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Set the environment variable `NUCLEARES_SERVER_URL` to the base URL of the game's webserver (for example `http://localhost:8080`) and run the application:

```bash
export NUCLEARES_SERVER_URL=http://localhost:8080
python app.py
```

The dashboard will be available at `http://localhost:5000`.

## Extending

- **Alarms**: adjust `ALARM_THRESHOLDS` in `app.py` or implement your own logic in `update_data`.
- **Graphs**: add additional datasets in `templates/dashboard.html` and store history in `app.py`.
- **Autonomous Mode**: create functions to send POST requests to the game server based on the current plant state.

For more information about the game and its variables, consult the official "NUCLEARES - User Manual" included in this repository.
