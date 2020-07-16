'''This is a web app (still in development)'''
import json
# import pprint
# import requests
import psycopg2
from flask import Flask, request, redirect, url_for, make_response, session, request #,jsonify
from flask_sqlalchemy import SQLAlchemy
from psycopg2 import sql
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from datetime import timedelta
cookie_duration = timedelta(days=1)

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=1)
app.config['SECRET_KEY']='yellowyellowdirtyfellowsogetredone'
ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:super@localhost/blogdata'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nmxwgggmawwwoc:daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd@ec2-34-206-31-217.compute-1.amazonaws.com:5432/dc2g7b9o8p5for'
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Posts(db.Model):
    '''This is a calss for Posts table'''
    __tablename__ = 'posts'
    _id = db.Column(db.Integer, primary_key=True,)
    title = db.Column(db.Text())
    content = db.Column(db.Text())
    author = db.Column(db.Text())

    def __init__(self, username, email):
        self.username = username
        self.email = email

class Users(db.Model,UserMixin):
    '''This is a calss for Users table'''
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text())
    email = db.Column(db.Text())
    passwd = db.Column(db.Text())

    def __init__(self, username, email, passwd):
        self.username = username
        self.email = email
        self.passwd = passwd
    def get_id(self):
        return self.user_id

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

def get_blog_posts():
    '''actual implementation of getting-fetching all blogs/posts from posts table'''
    try:
        if ENV == 'dev':
            conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
        else:
            conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
            # try:
        cur = conn.cursor()
        # cur.execute("SELECT json_agg(posts) FROM posts")
        # cur.execute("SELECT to_jsonb(array_agg(posts)) FROM posts")
        cur.execute("SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id,title, author) AS ColumnName (_id,title, author)))) FROM posts;")
        result = cur.fetchall()[0][0]
        conn.commit()
        cur.close()
        conn.close()
        print("from function")
        print(result)
        return result
    except psycopg2.OperationalError:
        return 500,{'Server Error':'Database Error'}
def fetch_post_by_id(id):
    '''actual implementation of getting-fetching post from posts table of gievn id'''
    try:
        if ENV == 'dev':
            conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
        else:
            conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
        cur = conn.cursor()
        cur.execute(f"SELECT json_agg(posts) FROM posts where _id = {id}")
        # cur.execute("SELECT to_jsonb(array_agg(posts)) FROM posts")
        result = cur.fetchall()[0][0][0]
        print('*')
        print(result)
        print('*')
        conn.commit()
        cur.close()
        conn.close()
        return result
    except TypeError as error:
        return 500,{'Server Error':f'{error}'}

def insert_post_to_database(title, content, author):
    '''actual implementation of insertion of data into posts table'''
    try:
        if ENV == 'dev':
            conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
        else:
            conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
        try:
            cur = conn.cursor()
            cur.execute('''select count(_id) from posts ''')
            newid = cur.fetchall()[0][0]
            print(newid)
            newid+=1
            query = sql.SQL('''insert into posts (_id, title, content, author) values (%s,%s, %s, %s)''')
            cur.execute(query, (newid,title, content, author))
            conn.commit()
            cur.close()
            conn.close()
            print('done posting post')
            return True
        except:
            print('failed posting post')
            return False
    except:
        print('failed to connect')
        return False

def delete_all():
    if ENV == 'dev':
        conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
    else:
        conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
    cur = conn.cursor()
    cur.execute('select count(*) from posts')
    n = cur.fetchall()[0][0]
    if n != 0:
        cur.execute("DELETE FROM posts")
        conn.commit()
        cur.close()
        conn.close()
        return make_response({"Response":"All Posts have been deleted!"})
    else:
        cur.close()
        conn.close()
        return make_response({'Response':'No posts no delete'})

def login_through_header():
    username='jay'
    passwd='1234'
    user = Users.query.filter_by(username=username,passwd=passwd).first()
    if user:
        login_user(user,duration=cookie_duration)
        return True
    else:
        return False

@app.route('/')
@app.route('/blog')
def blog_page():
    '''tempo blog page route'''
    admin = '(admin-login not found)'
    if current_user.is_authenticated:
        admin='(admin-login found)'
    return f"<div style='text-align:center;font-size:calc(100px - 6vw);'><h1>this is blog page</h1><br>{admin}<br><h3><br><br>see posts: <a href='/blog/posts'>/blog/posts</a><br>create a post: <a href='/blog/post'>/blog/post</a><br>admin login: <a href='/blog/admin'>/blog/admin</a></h3><div>"

@app.route('/blog/posts', methods=["GET"])
def return_blog_posts():
    '''displaying all posts data from posts table'''
    result = get_blog_posts()
    print('*************\nresult:')
    print(type(result))
    try:
        if result[0] == 500:
            if result[1]['Server Error'] == "Database Error":
                resp = make_response({'Server Error':'Database Connection Error'})
            else:
                resp = make_response({'Server Error':'Unknown Error'})
        else:
            resp = make_response({f'posts':result})
    except TypeError:
        if result is None:
            resp = make_response({'Server Error':'No Posts! Someone ate all the posts...'})
        else:
            resp = make_response({f'posts':result})
    finally:
        resp.mimetype = 'application/json'
        return resp

@app.route('/blog/posts/id=<int:id>')
def get_post_by_id(id):
    result=fetch_post_by_id(id)
    try:
        if result[0] == 500:
            if result[1]['Server Error'] == "'NoneType' object is not subscriptable":
                resp = make_response({'Server Error':f'The Post Does Not Exists'})
            else:
                resp = make_response({'Server Error':'Unknown Error'})
    except KeyError:
        resp = make_response({f'post {id}':result})
    finally:
        resp.mimetype = 'application/json'
        return resp

@app.route('/blog/post', methods=['POST'])
def upload_post():
    '''inserting data received from request form into posts table in db'''
    if current_user.is_authenticated:
        if 'title' in request.form and 'content' in request.form and 'author' in request.form:
            title = request.form['title']
            content = request.form['content']
            author = request.form['author']
            r = insert_post_to_database(title, content, author)
            if r:
                resp = make_response({'result':'post uploaded'})
                resp.mimetype = 'application/json'
                return resp
            else:
                resp = make_response({'result':'failed to upload post'})
                resp.mimetype = 'application/json'
                resp.status_code = 507
                return resp
        else:
            resp = make_response({'result':'required request not satisfied by form data'})
            resp.mimetype = 'application/json'
            resp.status_code = 507
            return resp
    else:
        return make_response({'response':'unathorized access'})

@app.route('/blog/post', methods=["GET"])
def upload_post_page():
    '''tempo route for uploading a new data post into db'''
    if current_user.is_authenticated:
        return '<br><br><br><br><br><hr><form style="text-align: center;line-height: 1.5;" action="/blog/post" method="POST"><p style="font-size:calc(130px - 8vw);">Create A Post</p><input style="font-size:calc(130px - 8vw);" type="text" name="title" placeholder="Enter Title" required /><br><input style="font-size:calc(130px - 8vw);" type="text" name="content" placeholder="Enter Content" required /><br><input type="text" name="author" placeholder="Enter Author" style="font-size:calc(130px - 8vw);" required><br><br><input style="font-size:calc(130px - 8vw);" type="submit" value="Post"></form><hr><form style="text-align: center;line-height: 1.5;" action="/blog/post/delete" method="POST"><input style="font-size:calc(130px - 8vw);" type="submit" value="Delete all posts"></form><hr>'
    else:
        return make_response({'response':'unathorized access'})

@app.route('/blog/post/delete', methods=["GET","POST"])
def delete_all_posts():
    if current_user.is_authenticated:
        return delete_all()
    else:
        return make_response({'response':'unathorized access'})

@app.route('/blog/login', methods=['POST'])
def blog_login():
    '''login route will perform login and send cookies via flask-login library'''
    try:
        header = request.headers['C_AUTH']
        if header == '?Rkqj98_hNV77aR67MRQhXz6_WC7XApXdG8@':
            login_through_header()
    finally:
        if not current_user.is_authenticated:
            if 'username' in request.form and 'passwd' in request.form:
                username = request.form.get('username')
                passwd = request.form.get('passwd')
                user = Users.query.filter_by(username=username,passwd=passwd).first()
                if user:
                    login_user(user,remember=True,duration=cookie_duration)
                    resp = make_response({'response':'logged in'})
                    resp.mimetype = 'application/json'
                    session.permanent = True
                    session['_id'] = user.user_id

                    return resp
                else:
                    resp = make_response({'Response':'User not Found!'})
                    resp.mimetype = 'application/json'
                    return resp
            else:
                return make_response({'response':'required fields did not match(username,password)'})
        else:
            return make_response({'Response':'Already Logged in'})

@app.route('/blog/admin', methods=['GET'])
def blog_admin_page():
    '''Tempo admin page'''
    if current_user.is_authenticated:
        return '<form style="text-align: center;" action="/blog/logout" method="POST" style="line-height: 1.5;"><p style="font-size:calc(200px - 10vw); margin-top:35vh;">Logout:</p><input style="font-size:calc(200px - 10vw);" type="submit" value="logout"></form>'
    return '<form style="text-align: center;" action="/blog/login" method="POST" style="line-height: 1.5;"><input style="font-size:calc(150px - 8vw);margin-top:35vh;" type="text" name="username" placeholder="Enter Name" required /><br><br><input type="password" name="passwd" placeholder="Enter Password" style="font-size:calc(150px - 8vw)" required><br><br><input style="font-size:calc(150px - 8vw)" type="submit" value="login"></form>'

@app.route('/blog/logout', methods=["POST"])
def blog_logout():
    if current_user.is_authenticated:
        session.pop("_id",None)
        logout_user()
        return make_response({'response':'logged out'})
    return make_response({'response':'not logged in'})

if __name__ == "__main__":
    db.create_all()
    app.run()