from flask import Flask, render_template, redirect, url_for, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import os
import datetime
from datetime import timedelta

from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token


# Setup default Flask Initial Status
app = Flask(__name__)
bcrypt = Bcrypt(app)
load_dotenv()
URL = os.environ.get('client')
client = MongoClient(URL)
db = client.makingchallenge

# Setup the Flask-JWT-Extended extension
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)


@app.route('/')
def show_index():
    # return render_template('index.html')
    return jsonify(a=test_123.a)


@app.route('/bucket/signup', methods=['POST'])
def signup():
    username_receive = request.form['username']
    password_receive = bcrypt.generate_password_hash(request.form['password'])
    if db.user.find_one({'username': username_receive}):
        return jsonify({'msg':'사용자가 이미 존재합니다'}), 401
    doc = {
        'username': username_receive,
        'password': password_receive,
        'user_num': len(list(db.user.find({},{'_id':False})))+1
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
    refresh_token = create_refresh_token(identity=username_receive)
    return jsonify({'msg':f'{username_receive}님 환영합니다', 'access_token': access_token, 'refresh_token': refresh_token}), 200


@app.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@app.route('/bucket/insert', methods=['POST'])
@jwt_required()
def insert_bucket():
    create_user = get_jwt_identity()
    if not create_user:
        return jsonify({"msg": "인증 헤더가 올바르지 않습니다!"}), 401
    bucket_receive = request.form['bucket'].strip()
    doc = {
        'username': create_user,
        'bucket': bucket_receive,
        'done': 0,
        'post_date': datetime.datetime.now().strftime('%Y%m%d-%H%M%S'),
        'bucket_num': len(list(db.bucket.find({"username":create_user},{"_id":False}))) + 1,
        'bucket_like': 0
    }
    db.bucket.insert_one(doc)
    return jsonify({"msg": "버킷이 등록되었습니다"}), 200


@app.route('/bucket/read')
@jwt_required()
def read_bucket():
    read_user = get_jwt_identity()
    if not read_user:
        return jsonify({"msg": "인증 헤더가 올바르지 않습니다"}), 401
    target_user = request.args.get("username")
    if target_user != read_user:
        return jsonify({"msg": "회원님의 정보가 올바르지 않습니다"}), 401
    target_bucket_list = list(db.bucket.find({"username":read_user},{"_id": False}))
    return jsonify({"bucket_list": target_bucket_list})


@app.route('/bucket/delete', methods=["POST"])
@jwt_required()
def delete_bucket():
    delete_user = get_jwt_identity()
    if not delete_user:
        return jsonify({'msg':'유효한 인증 사용자가 아닙니다'}), 401
    bucket_num_receive = int(request.form['bucket_num'])
    db.bucket.delete_one({'bucket_num': bucket_num_receive})
    return jsonify({'msg': '버킷 삭제에 성공했습니다'}), 200
    

@app.route('/bucket/edit', methods=['POST'])
@jwt_required()
def edit_bucket():
    edit_user = get_jwt_identity()
    if not edit_user:
        return jsonify({'msg': '유효한 인증 사용자가 아닙니다'}), 401
    bucket_num_receive = int(request.form['bucket_num'])
    bucket_edit_receive = request.form['bucket_edit']
    db.bucket.update_one({'bucket_num': bucket_num_receive}, {"$set":{'bucket': bucket_edit_receive}})
    return jsonify({'msg': '버킷 수정 완료!'}), 200

@app.route('/bucket/like', methods=['POST'])
@jwt_required()
def like_bucket():
    like_user = get_jwt_identity()
    if not like_user:
        return jsonify({'msg': '유효한 인증 사용자가 아닙니다'}), 401
    bucket_num_receive = int(request.form['bucket_num'])
    target_like = db.like.find_one({'like_user': like_user}, {'bucket_num': bucket_num_receive})
    if target_like:
        db.like.delete_one(target_like)
        return jsonify({'msg': '좋아요 취소!'})
    doc = {
        'like_user' : like_user,
        'bucket_num' : bucket_num_receive
    }
    db.like.insert_one(doc)
    return jsonify({'msg': '좋아요 완료!'})

if __name__ == "__main__":
    app.run('0.0.0.0',port=8080, debug=True)
           