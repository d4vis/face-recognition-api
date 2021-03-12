from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import MetaData, Table
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify
from flask_cors import cross_origin


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
    user_list = []
    for user in req:
        res = user.__dict__
        del res['_sa_instance_state']
        user_list.append(res)
    # user_list.sort(key=lambda k: k['id'])
    return jsonify(user_list)


app.run(debug=True)
