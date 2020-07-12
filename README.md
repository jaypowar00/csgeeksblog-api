# api-demo-private
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
## 2) /blog/admin
for admin previleges, must login for performing some adding or deleting posts operations !

## 3) /blog/post
Will insert the Title, Content, Author data into posts Table!

## 4) /blog/post/id=?
This route will fetch data for single post of mentioned _id from the database...(only int values accepted at '?')

# Web App Under Development!
This is still under developement ...
