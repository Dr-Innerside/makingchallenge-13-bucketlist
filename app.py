from flask import Flask, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
client = os.environ.get('client')

@app.route('/')
def show_index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run('0.0.0.0',port=8080, debug=True)
           