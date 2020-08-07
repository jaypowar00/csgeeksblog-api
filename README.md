# API using Python - Flask - Postgresql
(understand the code before running it blindly)

The app.py is like a skeleton!
(Created some temporary GET route for posting form data quickly!)

don't except 100% output without modiying it...
## 1) /blog/posts
This gets all the data from given table of from the database and return it in json format (array of objects)

e.g.
```
{
  "users" : [
  {
    "name":"user1",
    "email": "user1@example.com"
  },
  {
    "name":"user2",
    "email": "user2@example.com"
  }
  ]
}
```
this route also includes advanced queries!
+ ?order=  [either 'asc' or 'desc' | bydefault it's set to 'desc']
  This will decide in which order the query should give response json either in ascending or descending order.
+ ?orderby= [could have '_id','title','author','created' or 'description' | bydefault it's set to 'created']
  This will tell according to what basis the query should fetch the data from database.[bydefault it will fetch latest data first and oldest last]
+ ?author= [could have name of author | bydefault its None]
  This will fetch data for given author name from db
+ ?tag= [could have any tag value | bydefault its None]
  This will fetch all data whose tags matches the given tag.
  
(These queries can be combined together for more accuracy in response as per required!)

## 2) /blog/admin
for admin previleges, must login for performing some adding or deleting posts operations !

## 3) /blog/create
Will insert the Title, Author, Content, Description, Tags, Thumbnail_link data into posts Table!

Required fields for creation of post:
type -> form data - title
- author
- content
- description
- tags [needs to be array]
- thumbnail

## 4) /blog/post?id=
This route will fetch data for single post of mentioned _id from the database...

## 5) Login through C_AUTH header request
Added feature for logging in via header request (C_AUTH) with particular key value !

## 6) /blog/post/delete
This will delete all posts from db

query parameters:
+ ?id=  [It could be any existing post id]
  This will delete the post of given id from db

## 7) /blog/author
This route will give information about author if 'name' query parametr is given to this route.

query parameters:
+ ?name=  [it could have any available author name]
  This will fetch the information about given author name.
  
## 8) /blog/update
This will update the data values from the existing post of given 'id' parameter.

query parameters:
+ ?id= [it could be any existing post id]

Required fields for updation of post of given id:
type -> form data
- title
- author
- content
- description
- tags [needs to be array]
- thumbnail

# Web App Under Development!
This is still under developement ...
