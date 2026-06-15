from flask import Flask, jsonify, Response
from screener import run_screener

app = Flask(__name__)

@app.route("/")
def home():
    return "PRO SIGNAL ENGINE RUNNING"

@app.route("/run")
def run():
    return jsonify(run_screener())

@app.route("/run-html")
def run_html():
    data = run_screener()
    return Response(data["pretty_html"], mimetype="text/html")
