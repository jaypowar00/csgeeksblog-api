from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import json

app = Flask(__name__)

ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:super@localhost/userdata'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nmxwgggmawwwoc:daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd@ec2-34-206-31-217.compute-1.amazonaws.com:5432/dc2g7b9o8p5for'
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))

    def __init__(self,username,email):
        self.username = username
        self.email = email

@app.route('/')
def home():
    username = 'Jaypowar'
    email = 'jay@example.com'
    '''
    #for adding values in rows
    '''
    data = Users(username,email)
    db.session.add(data)
    '''
    #for removing rows by filtering them woth
    # Users.query.filter_by(username=username,email=email).first().delete()
    '''
    db.session.commit()
    return '1'

if __name__ == "__main__":
    db.create_all()
    app.run()
