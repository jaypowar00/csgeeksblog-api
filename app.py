import psycopg2
from flask import Flask, request,jsonify

DB_NAME = "d3aqjq8nk8in3e"
DB_USER = "rlujrnnlqazipq"
DB_PASS = "951370f7ecd7b589a9e00df2987b3c421c3d9476d872079f93d8085f4394510c"
DB_HOST = "ec2-52-70-15-120.compute-1.amazonaws.com"
DB_PORT = "5432"

def show_database():
    try:
        conn = psycopg2.connect(database = DB_NAME, user = DB_USER , password = DB_PASS, host =DB_HOST ,port = DB_PORT)
        cur = conn.cursor()

        cur.execute("SELECT json_agg(users) FROM users")
        cur.execute("SELECT to_jsonb(array_agg(users)) FROM users")

        result = cur.fetchall()[0][0]
        cur.close()
        conn.close()
        return result

    except:
        if conn.close == 0:
            cur.close()
            conn.close()
        return False

app = Flask(__name__)
@app.route('/',methods=["GET"])
def show():
    result = show_database()
    if (result != False):
        return jsonify(result),200
    else:
        return "database couldn't be read at this time..."

if __name__ == "__main__":
    app.run(debug=True)