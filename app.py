'''This is a web app (still in development)'''
import json
# import pprint
# import requests
import psycopg2
from flask import Flask, request, redirect, url_for, make_response, session #,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from psycopg2 import sql
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
import datetime
from time import gmtime, strftime
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
cookie_duration = timedelta(days=1)

app = Flask(__name__)
CORS(app)
app.permanent_session_lifetime = timedelta(days=1)
app.config['SECRET_KEY']='mysecretkey'
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
    '''This is a class for Posts table'''
    __tablename__ = 'posts'
    _id = db.Column(db.Integer, primary_key=True,)
    title = db.Column(db.Text())
    author = db.Column(db.Text())
    tags = db.Column(db.ARRAY(db.Text()))
    content = db.Column(db.Text())
    description = db.Column(db.Text())
    thumbnail = db.Column(db.Text())
    created = db.Column(db.DateTime(timezone=True),server_default=func.now())

    def __init__(self, title, content, author, description=None,tags=None):
        self.title = title
        self.content = content
        self.author = author
        self.desciption = description
        self.tags = tags

class Auther(db.Model):
    '''This is a class for Auther information'''
    __tablename__ = 'authors'
    auth_id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.Text())
    bio = db.Column(db.Text())
    mail = db.Column(db.Text())
    social = db.Column(db.ARRAY(db.Text()))

    def __init__(self,name,bio,mail,social):
        self.name = name
        self.bio = bio
        self.mail = mail
        self.social = social

class Users(db.Model,UserMixin):
    '''This is a class for Users table'''
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

def get_blog_posts(orderby='created' ,order='desc',author=None,tag=None):
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
        if author:
            if tag:
                cur.execute(f'''SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created) WHERE author='{author}' AND tags @> '{{"{tag}"}}')) ORDER BY {orderby} {order}) FROM posts;''')
            else:
                cur.execute(f'''SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created) WHERE author='{author}')) ORDER BY {orderby} {order}) FROM posts;''')
        elif tag:
            cur.execute(f'''SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created) WHERE tags @> '{{"{tag}"}}')) ORDER BY {orderby} {order}) FROM posts;''')
        else :
            cur.execute(f"SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id, title, description, author, tags, thumbnail, created) AS ColumnName (_id, title, description, author, tags, thumbnail, created))) ORDER BY {orderby} {order}) FROM posts;")
        # cur.execute("SELECT json_agg(row_to_json(t) FROM (select _id,title,description,author,tags,thumbnail,created FROM posts) t);")
        result = cur.fetchall()[0][0]
        result = list(filter(None, result))
        conn.commit()
        cur.close()
        conn.close()
        # print("from function")
        # print(result)
        return result
    except psycopg2.OperationalError:
        return 500,{'Server Error':'Database Error'}
    except psycopg2.errors.UndefinedColumn:
        return 500,{'Server Error':'Invalid Orderby'}

def getadmindata(name):
    try:
        if ENV == 'dev':
            conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
        else:
            conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
            # try:
        cur = conn.cursor()
        cur.execute(f"SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT auth_id,name,bio,mail,social) AS ColumnName (auth_id,name,bio,mail,social)))) FROM authors where name = '{name}' ;")
        result = cur.fetchall()[0][0]
        conn.commit()
        cur.close()
        conn.close()
        # print("from function admin")
        # print(result)
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
        # print('*')
        # print(result)
        # print('*')
        conn.commit()
        cur.close()
        conn.close()
        return result
    except TypeError as error:
        return 500,{'Server Error':f'{error}'}

def insert_post_to_database(title, content, description, tags, thumbnail, author):
    '''actual implementation of insertion of data into posts table'''
    try:
        if ENV == 'dev':
            conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
        else:
            conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
        try:
            cur = conn.cursor()
            # cur.execute('''select count(_id) from posts ''')
            # newid = cur.fetchall()[0][0]
            # # print(newid)
            # newid+=1
            query = sql.SQL('''insert into posts (title, content, description, tags, thumbnail, author) values (%s,%s,%s,%s,%s,%s)''')
            cur.execute(query, (title, content, description, tags, thumbnail, author))
            conn.commit()
            cur.close()
            conn.close()
            # print('done posting post')
            return True
        except:
            # print('failed posting post')
            return False
    except:
        # print('failed to connect')
        return False

def update_post_by_id(id,title, content, description, tags, thumbnail, author):
    '''actual implementation of updation of post'''
    try:
        if ENV == 'dev':
            conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
        else:
            conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
        try:
            cur = conn.cursor()
            query = sql.SQL('''UPDATE posts SET title=%s, content=%s, description=%s, tags=%s, thumbnail=%s, author=%s WHERE _id=%s''')
            cur.execute(query, (title, content, description, tags, thumbnail, author,id))
            conn.commit()
            cur.close()
            conn.close()
            # print('done posting post')
            return True
        except:
            # print('failed posting post')
            return False
    except:
        # print('failed to connect')
        return False

def postadmindata(name,bio,mail,social):
    '''tempo '''
    try:
        if ENV == 'dev':
            conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
        else:
            conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
        try:
            cur = conn.cursor()
            query = sql.SQL('''insert into authors (name,bio,mail,social) values (%s,%s,%s,%s)''')
            cur.execute(query, (name,bio,mail,social))
            conn.commit()
            cur.close()
            conn.close()
            # print('done posting admin')
            return True
        except:
            # print('failed posting admin')
            return False
    except:
        # print('failed to connect')
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
        return make_response({"response":"All Posts have been deleted!"})
    else:
        cur.close()
        conn.close()
        return make_response({'response':'No posts to delete'})

def delete_by(id):
    if ENV == 'dev':
        conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
    else:
        conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
    cur = conn.cursor()
    cur.execute('select count(*) from posts')
    n = cur.fetchall()[0][0]
    if n != 0:
        cur.execute(f"DELETE FROM posts WHERE _id={id}")
        conn.commit()
        cur.close()
        conn.close()
        return make_response({"response":"The Post have been deleted!"})
    else:
        cur.close()
        conn.close()
        return make_response({'response':'No posts to delete'})

def check_pass_hash(username,password):
    try:
        if ENV == 'dev':
            conn = psycopg2.connect(database="blogdata", user="postgres", password="super", host="localhost", port="5432")
        else:
            conn = psycopg2.connect(database="dc2g7b9o8p5for", user="nmxwgggmawwwoc", password="daeaa787dea0c53a312eedf9b4601f7cff2973e603eec3e27c8fc782d133f7bd", host="ec2-34-206-31-217.compute-1.amazonaws.com", port="5432")
        cur = conn.cursor()
        cur.execute("SELECT json_agg(users) FROM users")
        # cur.execute("SELECT to_jsonb(array_agg(posts)) FROM posts")
        # cur.execute("SELECT json_agg(row_to_json((SELECT ColumnName FROM (SELECT _id,title, author) AS ColumnName (_id,title, author)))) FROM posts;")
        result = cur.fetchall()[0][0]
        conn.commit()
        cur.close()
        conn.close()
        # print("from users:")
        # print(result)
        for x in result:
            if x['username']==username and check_password_hash(x['passwd'],password):
                # print(x['user_id'])
                return x['user_id']
        return False
    except psycopg2.OperationalError:
        return 500,{'Server Error':'Database Error'}

def login_through_header():
    username='jay'
    passwd='1234'
    u_id = check_pass_hash(username,passwd)
    if u_id:
        # print("hash true")
        user = Users.query.filter_by(username=username,user_id=u_id).first()
    # else:
        # print("hash false")
    if user:
        login_user(user,remember=True,duration=cookie_duration)
        return True
    else:
        return False

@app.route('/')
@app.route('/blog')
def blog_page():
    '''tempo blog page route'''
    db.create_all()
    admin = '(admin-login not found)'
    header = ''
    try:
            header = request.headers['C_AUTH']
    finally:
        if current_user.is_authenticated or header == '?Rkqj98_hNV77aR67MRQhXz6_WC7XApXdG8@' :
            admin='(admin-login found)'
        return f"<div style='text-align:center;font-size:calc(100px - 6vw);'><h1>this is blog page</h1><br>{admin}<br><h3><br><br>see posts: <a href='/blog/posts'>/blog/posts</a><br>create a post: <a href='/blog/create'>/blog/create</a><br>admin login: <a href='/blog/admin'>/blog/admin</a></h3><div>"

@app.route('/blog/posts', methods=["GET"])
def return_blog_posts():
    '''displaying all posts data from posts table'''
    db.create_all()
    in_query = request.args
    if in_query:
        if 'orderby' in in_query or 'order' in in_query or 'author' in in_query or 'tag' in in_query:
            if 'orderby' in in_query and 'order' in in_query and 'author' in in_query and 'tag' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(orderby=in_query["orderby"],order=in_query["order"],author=in_query['author'],tag=in_query['tag'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'order' in in_query and 'orderby' in in_query and 'author' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(orderby=in_query["orderby"],order=in_query["order"],author=in_query['author'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'order' in in_query and 'orderby' in in_query and 'tag' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(orderby=in_query["orderby"],order=in_query["order"],tag=in_query['tag'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'order' in in_query and 'tag' in in_query and 'author' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(order=in_query["order"],author=in_query['author'],tag=in_query['tag'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'tag' in in_query and 'author' in in_query:
                result = get_blog_posts(orderby=in_query["orderby"],author=in_query['author'],tag=in_query['tag'])
            elif 'author' in in_query and 'tag' in in_query:
                result = get_blog_posts(author=in_query['author'],tag=in_query['tag'])
            elif 'order' in in_query and 'tag' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(order=in_query['order'],tag=in_query['tag'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'tag' in in_query:
                result = get_blog_posts(order=in_query['order'],tag=in_query['tag'])
            elif 'order' in in_query and 'author' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(order=in_query['order'],author=in_query['author'])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query and 'author' in in_query:
                result = get_blog_posts(orderby=in_query['orderby'],author=in_query['author'])
            elif 'author' in in_query :
                result = get_blog_posts(author=in_query['author'])
            elif 'tag' in in_query :
                result = get_blog_posts(tag=in_query['tag'])
            elif 'orderby' in in_query and 'order' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(orderby=in_query["orderby"],order=in_query["order"])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameters'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'orderby' in in_query:
                result = get_blog_posts(orderby=in_query["orderby"])
            elif 'order' in in_query:
                if in_query['order']=='desc' or in_query['order']=='asc' :
                    result = get_blog_posts(order=in_query["order"])
                else:
                    resp = make_response({'success':False,'Server Error':'invalid value for "order" query parameter'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'author' in in_query:
                if in_query['author'].lower()=='aeyjey' or in_query['author'].lower() =='redranger' or in_query['author'].lower() == 'whoknows' :
                    result = get_blog_posts(author=in_query['author'])
                else:
                    resp = make_response({'success':False,'Server Error':'Author does not exists.'})
                    resp.mimetype = 'application/json'
                    return resp
            elif 'tag' in in_query:
                result = get_blog_posts(tag=in_query['tag'])
        else:
            resp = make_response({'success':False,'Server Error':'invalid query parameter(s)'})
            resp.mimetype = 'application/json'
            return resp
    else:
        result = get_blog_posts()
    # print('*************\nresult:')
    # print(type(result))
    try:
        if result[0] == 500:
            if result[1]['Server Error'] == "Database Error":
                resp = make_response({'success':False,'Server Error':'Database Connection Error'})
            elif result[1]['Server Error'] == "Invalid Orderby":
                resp = make_response({'success':False,'Server Error':'Invalid value for "orderby" query parameter'})
            else:
                resp = make_response({'success':False,'Server Error':'Unknown Error'})
        else:
            resp = make_response({'success':True,f'articles':result})
    except TypeError:
        if result is None:
            resp = make_response({'success':False,'Server Error':'No Posts! Someone ate all the posts...'})
        else:
            resp = make_response({'success':True,f'articles':result})
    except IndexError:
        if len(result) == 0 :
            resp = make_response({'success':False,'Server Error':'No Posts for given filter!...'})
    finally:
        resp.mimetype = 'application/json'
        return resp

@app.route('/blog/post')
def get_post_by_id():
    id = request.args
    if 'id' in id:
        print(id['id'])
        id = id['id']
        db.create_all()
        result=fetch_post_by_id(id)
        try:
            if result[0] == 500:
                if result[1]['Server Error'] == "'NoneType' object is not subscriptable":
                    resp = make_response({'success':False,'Server Error':f'The Post Does Not Exists'})
                else:
                    resp = make_response({'success':False,'Server Error':'Unknown Error'})
        except KeyError:
            resp = make_response({'success':True,f'article':result})
        finally:
            resp.mimetype = 'application/json'
            return resp
    resp = make_response({'success':False,'Server Error':'missing query'})
    resp.mimetype = 'application/json'
    return resp

@app.route('/blog/create', methods=['POST'])
def upload_post():
    '''inserting data received from request form into posts table in db'''
    db.create_all()
    header = ''
    try:
            header = request.headers['C_AUTH']
    finally:
        if current_user.is_authenticated or header == '?Rkqj98_hNV77aR67MRQhXz6_WC7XApXdG8@' :
            if 'title' in request.form and 'content' in request.form and 'author'  in request.form and 'thumbnail' in request.form and 'tags' in request.form :
                title = request.form['title']
                content = request.form['content']
                author = request.form['author']
                tags = request.form['tags'].split(",")
                description = None
                thumbnail = None
                if request.form['description'] != "" :
                    description = request.form['description']
                if request.form['thumbnail'] != "" :
                    thumbnail = request.form['thumbnail']
                r = insert_post_to_database(title, content, description, tags, thumbnail, author)
                if r:
                    resp = make_response({'success':True,'result':'post uploaded'})
                    resp.mimetype = 'application/json'
                    return resp
                else:
                    resp = make_response({'success':False,'result':'failed to upload post'})
                    resp.mimetype = 'application/json'
                    resp.status_code = 500
                    return resp
            else:
                resp = make_response({'success':False,"result":"missing form data for 'title','content','author' in the request"})
                resp.mimetype = 'application/json'
                resp.status_code = 500
                return resp
        else:
            return make_response({'success':False,'response':'unathorized access'})

@app.route('/blog/update', methods=['POST'])
def update_post():
    '''inserting data received from request form into posts table in db'''
    db.create_all()
    id = request.args
    if 'id' in id:
        id = id['id']
        header = ''
        try:
                header = request.headers['C_AUTH']
        finally:
            if current_user.is_authenticated or header == '?Rkqj98_hNV77aR67MRQhXz6_WC7XApXdG8@' :
                if 'title' in request.form and 'content' in request.form and 'author'  in request.form and 'thumbnail' in request.form and 'tags' in request.form :
                    title = request.form['title']
                    content = request.form['content']
                    author = request.form['author']
                    tags = request.form['tags'].split(",")
                    description = None
                    thumbnail = None
                    if request.form['description'] != "" :
                        description = request.form['description']
                    if request.form['thumbnail'] != "" :
                        thumbnail = request.form['thumbnail']
                    r = update_post_by_id(id,title, content, description, tags, thumbnail, author)
                    if r:
                        resp = make_response({'success':True,'result':'post updated'})
                        resp.mimetype = 'application/json'
                        return resp
                    else:
                        resp = make_response({'success':False,'result':'failed to update post'})
                        resp.mimetype = 'application/json'
                        resp.status_code = 500
                        return resp
                else:
                    resp = make_response({'success':False,"result":"missing form data for 'title','content','author' in the request"})
                    resp.mimetype = 'application/json'
                    resp.status_code = 500
                    return resp
            else:
                return make_response({'success':False,'response':'unathorized access'})
    else:
        return make_response({'success':False,'response':'missing value of id'})

@app.route('/blog/create', methods=["GET"])
def upload_post_page():
    '''tempo route for uploading a new data post into db'''
    db.create_all()
    header = ''
    try:
            header = request.headers['C_AUTH']
    finally:
        if current_user.is_authenticated or header == '?Rkqj98_hNV77aR67MRQhXz6_WC7XApXdG8@' :
            return '<br><br><br><br><br><hr><form style="text-align: center;line-height: 1.5;" action="/blog/create" method="POST"><p style="font-size:calc(130px - 8vw);">Create A Post</p><input style="font-size:calc(130px - 8vw);" type="text" name="title" placeholder="Enter Title" required /><br><input style="font-size:calc(130px - 8vw);" type="text" name="content" placeholder="Enter Content" required /><br><input type="text" name="author" placeholder="Enter Author" style="font-size:calc(130px - 8vw);" required><br><input type="text" name="description" placeholder="Enter Description" style="font-size:calc(130px - 8vw);"><br><input type="text" name="thumbnail" placeholder="Enter Link to thumnail" style="font-size:calc(130px - 8vw);"><br><br><input style="font-size:calc(130px - 8vw);" type="submit" value="Post"></form><hr><form style="text-align: center;line-height: 1.5;" action="/blog/post/delete" method="POST"><input style="font-size:calc(130px - 8vw);" type="submit" value="Delete all posts"></form><hr>'
        else:
            return make_response({'success':False,'response':'unathorized access'})

@app.route('/blog/post/delete', methods=["GET","POST"])
def delete_all_posts():
    db.create_all()
    id = request.args
    if 'id' in id:
        id = id['id']
        try:
            id = float(id)
            id = int(id)
        except:
            id = None
        finally:
            header = ''
            try:
                header = request.headers['C_AUTH']
            finally:
                if current_user.is_authenticated or header == '?Rkqj98_hNV77aR67MRQhXz6_WC7XApXdG8@' :
                    if id:
                        return delete_by(id)
                    else:
                        return make_response({'success':False,'response':'invalid post id'})
                    return delete_all()
                else:
                    return make_response({'success':False,'response':'unathorized access'})
    else:
        header = ''
        try:
            header = request.headers['C_AUTH']
        finally:
            if current_user.is_authenticated or header == '?Rkqj98_hNV77aR67MRQhXz6_WC7XApXdG8@' :
                return delete_all()
            else:
                return make_response({'response':'unathorized access'})


@app.route('/blog/login', methods=['POST'])
def blog_login():
    '''login route will perform login and send cookies via flask-login library'''
    db.create_all()
    try:
        if not current_user.is_authenticated:
            header = request.headers['C_AUTH']
            if header == '?Rkqj98_hNV77aR67MRQhXz6_WC7XApXdG8@':
                login_through_header()
    finally:
        if not current_user.is_authenticated:
            if 'username' in request.form and 'passwd' in request.form:
                username = request.form.get('username')
                passwd = request.form.get('passwd')
                u_id = check_pass_hash(username,passwd)
                if u_id:
                    # print("hash true")
                    user = Users.query.filter_by(username=username,user_id=u_id).first()
                else:
                    user = False
                    # print("hash false")
                if user:
                    login_user(user,remember=True,duration=cookie_duration)
                    resp = make_response({'success':True,'response':'logged in'})
                    resp.mimetype = 'application/json'
                    session.permanent = True
                    session['_id'] = user.user_id
                    return resp
                else:
                    resp = make_response({'success':False,'response':'User not Found!'})
                    resp.mimetype = 'application/json'
                    return resp
            else:
                return make_response({'success':False,'response':'required fields did not match(username,password)'})
        else:
            return make_response({'success':True,'response':'Already Logged in'})

@app.route('/blog/admin', methods=['GET'])
def blog_admin_page():
    '''Tempo admin page'''
    db.create_all()
    if current_user.is_authenticated:
        return '<form style="text-align: center;" action="/blog/logout" method="POST" style="line-height: 1.5;"><p style="font-size:calc(200px - 10vw); margin-top:35vh;">Logout:</p><input style="font-size:calc(200px - 10vw);" type="submit" value="logout"></form>'
    return '<form style="text-align: center;" action="/blog/login" method="POST" style="line-height: 1.5;"><input style="font-size:calc(150px - 8vw);margin-top:35vh;" type="text" name="username" placeholder="Enter Name" required /><br><br><input type="password" name="passwd" placeholder="Enter Password" style="font-size:calc(150px - 8vw)" required><br><br><input style="font-size:calc(150px - 8vw)" type="submit" value="login"></form>'

@app.route('/blog/author', methods=['POST','GET'])
def admin_info():
    '''Tempo admin page'''
    db.create_all()
    name = request.args
    if 'name' in name:
        name = name['name']
        data = getadmindata(name)
        if data :
            resp = make_response({'success':True,f'author':data})
            resp.mimetype = 'application/json'
            return resp
        else:
            resp = make_response({'success':False,f'response':'author does not exist'})
            resp.mimetype = 'application/json'
            return resp
    resp = make_response({'success':False,f'response':'missing query'})
    resp.mimetype = 'application/json'
    return resp

# @app.route('/blog/authorcreate', methods=['GET'])
# def admin_info_post():
#     '''Tempo admin page'''
#     db.create_all()
#     name = 'jay'
#     bio = 'geek'
#     mail = 'example@gmail.com'
#     # instagram:https://www.instagram.com/_redranger00_/,
#     # twitter:https://twitter.com/jay_powar?s=09,
#     # github:https://github.com/jaypowar00
#     social = [['instagram','twitter','github'],['https://www.instagram.com/_redranger00_/','https://twitter.com/jay_powar?s=09','https://github.com/jaypowar00']]
#     data = postadmindata(name,bio,mail,social)
#     return '<h1>post data</h1>'

@app.route('/blog/logout', methods=["POST"])
def blog_logout():
    db.create_all()
    if current_user.is_authenticated:
        session.pop("_id",None)
        logout_user()
        return make_response({'response':'logged out'})
    return make_response({'response':'not logged in'})

if __name__ == "__main__":
    db.create_all()
    app.run()