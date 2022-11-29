from flask import Flask, render_template, redirect, url_for, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

load_dotenv()
URL = os.environ.get('client')
client = MongoClient(URL)
db = client.makingchallenge

@app.route('/')
def show_index():
    return render_template('index.html')

@app.route('/bucket/signup', methods=['POST'])
def signup():
    username_receive = request.form['username']
    password_receive = bcrypt.generate_password_hash(request.form['password'])

    doc = {
        'username': username_receive,
        'password': password_receive
    }
    db.user.insert_one(doc)
    

    return jsonify({"msg": "회원가입에 성공했습니다!"})

if __name__ == "__main__":
    app.run('0.0.0.0',port=8080, debug=True)
           