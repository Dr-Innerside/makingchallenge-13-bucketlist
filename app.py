from flask import Flask, render_template, redirect, url_for, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import os

from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_access_token

app = Flask(__name__)
bcrypt = Bcrypt(app)

load_dotenv()
URL = os.environ.get('client')
client = MongoClient(URL)
db = client.makingchallenge

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = os.environ.get('SECRET_KEY')
jwt = JWTManager(app)


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
    return jsonify({"msg": "회원가입에 성공했습니다!"}), 200

@app.route('/bucket/login', methods=['POST'])
def login():
    username_receive = request.form['username']
    password_receive = request.form['password']
    password_data = db.user.find_one({'username':username_receive},{'_id':False})['password']
    is_password_correct = bcrypt.check_password_hash(password_data, password_receive)
    if not is_password_correct:
        return jsonify({'msg': '아이디, 비밀번호가 다릅니다'}), 401
    
    access_token = create_access_token(identity=username_receive)
    return jsonify({'msg':f'{username_receive}님 환영합니다', 'access_token': access_token}), 200

@app.route('/bucket/insert', methods=['POST'])
@jwt_required()
def check_auth():
    create_user = get_jwt_identity()
    if not create_user:
        return jsonify({"msg": "인증 헤더가 올바르지 않습니다!"}), 401
    return redirect(url_for('show_index'))
    

if __name__ == "__main__":
    app.run('0.0.0.0',port=8080, debug=True)
           