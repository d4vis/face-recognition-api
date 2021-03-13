from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import MetaData, Table
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from flask_cors import cross_origin
import bcrypt
from datetime import datetime


def remove_sa_instance_state(data_object):
    del data_object['_sa_instance_state']
    return data_object


def request_to_dict(query_object):
    return list(map(remove_sa_instance_state, [user.__dict__ for user in query_object]))


app = Flask(__name__)
db_string = 'postgresql://postgres:123123qQ@localhost/smartbrain'
engine = create_engine(db_string, echo=False)

Base = declarative_base()
metadata = MetaData()


class User(Base):
    __table__ = Table('users', metadata, autoload_with=engine)


class Login(Base):
    __table__ = Table('login', metadata, autoload_with=engine)


metadata.create_all(engine)
Session = sessionmaker()
session = Session(bind=engine)


@app.route('/', methods=['GET'])
@cross_origin()
def all_users():
    req = session.query(User).all()
    user_list = request_to_dict(req)
    return jsonify(user_list)


@app.route('/signin', methods=['POST'])
@cross_origin()
def signin():
    user = request.json
    query = session.query(Login).filter(Login.email == user['email']).all()
    try:
        login_cred = request_to_dict(query)[0]
    except IndexError:
        return jsonify('invalid login/password'), 400
    hashed = login_cred['hash'].encode('utf-8')
    post_password = user['password'].encode('utf-8')
    isValid = bcrypt.checkpw(post_password, hashed)
    if isValid:
        try:
            query = session.query(User).filter(
                User.email == user['email']).all()
            user_cred = request_to_dict(query)[0]
            return jsonify(user_cred)
        except IndexError:
            return jsonify('unable to get user from database'), 400
    else:
        return jsonify('invalid login/password'), 400


@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    user = request.json
    hashed_pw = bcrypt.hashpw(user['password'].encode(
        'utf-8'), bcrypt.gensalt()).decode('utf-8')
    insertion_user = User(
        email=user['email'], name=user['name'], joined=datetime.now())
    login_user = Login(email=user['email'], hash=hashed_pw)
    try:
        session.add_all([insertion_user, login_user])
        session.commit()
    except:
        session.rollback()
    try:
        inserted_user = session.query(User).filter(
            User.email == user['email']).all()
        user_list = request_to_dict(inserted_user)[0]
        return jsonify(user_list)
    except IndexError:
        return jsonify('unable to register user'), 400


@app.route('/profile/<id>', methods=['GET'])
@cross_origin()
def profile(id):
    req = session.query(User).filter(User.id == id).all()
    try:
        user_list = request_to_dict(req)[0]
        return jsonify(user_list)
    except IndexError:
        return jsonify('Profile not found'), 400


@app.route('/image', methods=['PUT'])
@cross_origin()
def image():
    user_id = request.json['id']
    try:
        session.query(User).filter(User.id == user_id).update(
            {User.entries: User.entries + 1})
        session.commit()
    except:
        session.rollback()
    updated_entries = session.query(User).filter(User.id == user_id).all()
    try:
        entries = request_to_dict(updated_entries)[0]
        return jsonify(entries['entries'])
    except IndexError:
        return jsonify('unable to get entries'), 400


if __name__ == '__main__':
    app.run(debug=True)
