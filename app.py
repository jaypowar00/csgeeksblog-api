from flask import Flask, request,jsonify,redirect,url_for
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

class Posts(db.Model):
    __tablename__ = 'posts'
    _id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String())
    content = db.Column(db.String())
    author = db.Column(db.String())

    def __init__(self,username,email):
        self.username = username
        self.email = email

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.Text())
    email = db.Column(db.Text())
    passwd = db.Column(db.Text())

    def __ini__(self,username,email,passwd):
        self.username = username
        self.email = email
        self.passwd = passwd

def get_blog_posts():
    try:
        conn = psycopg2.connect(database = "dc2g7b9o8p5for", user = "nmxwgggmawwwoc" , password = "daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host ="ec2-34-206-31-217.compute-1.amazonaws.com" ,port = "5432")
        try:
            cur = conn.cursor()
            cur.execute("SELECT json_agg(posts) FROM posts")
            cur.execute("SELECT to_jsonb(array_agg(posts)) FROM posts")
            result = cur.fetchall()[0][0]
            conn.commit()
            cur.close()
            conn.close()
            return result
        except:
            return False
    except:
        return False


@app.route('/')
@app.route('/blog')
def blog_page():
    return '''<h1>this is blog page</h1><br><h3><br><br><a href='/blog/posts'>/blog/posts</a><br><a href='/blog/login'>/blog/login</a></h3>'''

@app.route('/blog/posts',methods=["GET"])
def return_blog_posts():
    result = get_blog_posts()
    if result != False:
        json_result = {"posts":result}
        newresult = json.dumps(json_result)
        return newresult,200
    else:
        return 'some error',506

@app.route('/blog/login',methods=['POST'])
def blog_login():
    if 'username' in request.form and 'passwd' in request.form:
        username = request.form['username']
        passwd = request.form['passwd']
        found_user = Users.query.filter_by(username=username,passwd=passwd).count() == 1
        return json.dumps(found_user).lower()
    else:
        redirect(url_for('blog_login_page'))


@app.route('/blog/login',methods=['GET'])
def blog_login_page():
    return '<br><br><br><br><br><form style="text-align: center;" action="#" method="POST" style="line-height: 1.5;"><input style="font-size:3vw;" type="text" name="username" placeholder="Enter Name" required /><br><input type="password" name="passwd" placeholder="Enter Password" style="font-size:3vw;" required><br><input style="font-size:3vw;" type="submit" value="login"></form>'

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)