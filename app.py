from flask import Flask, render_template
import os
import pandas as pd
import plotly.express as px
from collections import defaultdict
import re

app = Flask(__name__)

# Ensure correct file path
file_path = "logfile.txt"

def process_log():
    """ Extracts and processes log data from the logfile """
    if not os.path.exists(file_path):
        return [], [], 0  # Return empty data if logfile.txt is missing

    ip_counts = defaultdict(int)
    hour_counts = defaultdict(int)
    total_requests = 0

    with open(file_path, "r") as file:
        for line in file:
            ip_address = line.split()[0]  # Extract IP
            
            timestamp_match = re.search(r"\[(.*?)\]", line)
            if timestamp_match:
                hour_part = timestamp_match.group(1).split(":")[1]  # Extract hour
                ip_counts[ip_address] += 1
                hour_counts[hour_part] += 1
                total_requests += 1
    
    # Sort data
    sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    sorted_hours = sorted(hour_counts.items())

    return sorted_ips, sorted_hours, total_requests

def plot_ip_histogram(ip_data):
    """ Creates an interactive histogram for top IPs """
    if not ip_data:
        return ""  # Return empty if no data
    df = pd.DataFrame(ip_data, columns=["IP Address", "Requests"])
    fig = px.bar(df, x="IP Address", y="Requests", title="Top 10 IP Addresses", text="Requests")
    return fig.to_html(full_html=False)

def plot_hourly_histogram(hour_data):
    """ Creates an interactive histogram for hourly traffic """
    if not hour_data:
        return ""  # Return empty if no data
    df = pd.DataFrame(hour_data, columns=["Hour", "Requests"])
    fig = px.bar(df, x="Hour", y="Requests", title="Hourly Traffic", text="Requests")
    return fig.to_html(full_html=False)

@app.route("/")
def dashboard():
    """ Dashboard route to display data """
    ip_data, hour_data, total_requests = process_log()
    ip_chart = plot_ip_histogram(ip_data)
    hour_chart = plot_hourly_histogram(hour_data)

    return f"""
    <html>
    <head>
        <title>Log Analysis Dashboard</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
            .container {{ max-width: 800px; margin: auto; padding: 20px; }}
            .card {{ margin-bottom: 20px; padding: 20px; }}
            img {{ width: 100%; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center mt-4">📊 Server Log Analysis Dashboard</h1>
            <p class="text-center">Total Requests: <strong>{total_requests}</strong></p>

            <div class="card shadow">
                <h3 class="text-center">Top 10 IP Addresses</h3>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>IP Address</th>
                            <th>Requests</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f"<tr><td>{ip}</td><td>{count}</td></tr>" for ip, count in ip_data)}
                    </tbody>
                </table>
                {ip_chart}
            </div>

            <div class="card shadow">
                <h3 class="text-center">Hourly Traffic</h3>
                {hour_chart}
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)
