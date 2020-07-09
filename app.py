from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2 , json , pprint , requests

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
    __tablename__ = 'posts'
    _id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String())
    content = db.Column(db.String())
    author = db.Column(db.String())

    def __init__(self,username,email):
        self.username = username
        self.email = email

def get_blog_posts():
    try:
        conn = psycopg2.connect(database = "dc2g7b9o8p5for", user = "nmxwgggmawwwoc" , password = "daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host ="ec2-34-206-31-217.compute-1.amazonaws.com" ,port = "5432")
        try:
            print("before cursor")
            cur = conn.cursor()
            print("curson set...")
            cur.execute("SELECT json_agg(posts) FROM posts")
            cur.execute("SELECT to_jsonb(array_agg(posts)) FROM posts")
            result = cur.fetchall()[0][0]
            conn.commit()
            # print(result)
            cur.close()
            conn.close()
            return result
        except:
            print('after connection error')
            return False
    except:
        print('connection error')
        return False


@app.route('/')
@app.route('/blog')
def add():
    return "<h1>this is blog page</h1><br><h3>go to /blog/posts</h3>"

@app.route('/blog/posts',methods=["GET"])
def return_blog_posts():
    result = get_blog_posts()
    if result != False:
        json_result = {"posts":result}
        # print(json.dumps(json_result))
        newresult = json.dumps(json_result)
        return newresult,200
    else:
        return 'some error',506

# username = 'Jaypowar'
# email = 'jay@example.com'
# data = Users(username,email)
# db.session.add(data)
# db.session.commit()
# @app.route('/delete')
# def delt():
#     username = 'Jaypowar'
#     email = 'jay@example.com'
#     Users.query.filter_by(username=username,email=email).delete()
#     db.session.commit()
#     return 'deleted everything'

if __name__ == "__main__":
    db.create_all()
    app.run()