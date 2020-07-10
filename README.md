# api-demo-private
# API using Python - Flask - Postgresql
(understand the code before running it blindly)

The app.py is like a skeleton!

don't except 100% output without modiying it...
## 1)
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
## 2)
Got login route which will check the user info received from a form submit and will chec with the database (users table), if found then will return true, if not then false...


This is still under developement ...
