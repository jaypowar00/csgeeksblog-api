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
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))

    def __init__(self,username,email):
        self.username = username
        self.email = email
    # @property
    # def serialize(self):
    #     '''return object in serialized format'''
    #     return {
    #         'id':self.id,
    #         'username':self.username,
    #         'email':self.email
    #     }
    # @property
    # def serialize_many2many(self):
    #     return [item.serialize for item in self.many2many]


# DB_NAME = "d3aqjq8nk8in3e"
# DB_USER = "rlujrnnlqazipq"
# DB_PASS = "951370f7ecd7b589a9e00df2987b3c421c3d9476d872079f93d8085f4394510c"
# DB_HOST = "ec2-52-70-15-120.compute-1.amazonaws.com"
# DB_PORT = "5432"

# def show_database():
#     try:
#         conn = psycopg2.connect(database = DB_NAME, user = DB_USER , password = DB_PASS, host =DB_HOST ,port = DB_PORT)
#         cur = conn.cursor()

#         cur.execute("SELECT json_agg(users) FROM users")
#         cur.execute("SELECT to_jsonb(array_agg(users)) FROM users")

#         result = cur.fetchall()[0][0]
#         cur.close()
#         conn.close()
#         return result

#     except:
#         if conn.close == 0:
#             cur.close()
#             conn.close()
#         return False

# @app.route('/')
# def show():
    # result = show_database()
    # if (result != False):
    #     return jsonify(result),200
    # else:
    #     return "database couldn't be read at this time..."

@app.route('/')
def home():
    username = 'Jaypowar'
    email = 'jay@example.com'
    data = Users(username,email)
    db.session.add(data)
    # Users.query.filter_by(username=username,email=email).delete()
    db.session.commit()
    return '1'

if __name__ == "__main__":
    app.run()