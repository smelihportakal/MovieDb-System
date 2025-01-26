from flask import  Flask,render_template,request, redirect, session
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.secret_key = "secret"

db = yaml.safe_load(open('db.yaml'))
app.config["MYSQL_HOST"] = db["MYSQL_HOST"] 
app.config["MYSQL_USER"] = db["MYSQL_USER"]
app.config['MYSQL_PASSWORD'] = db['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = db['MYSQL_DB']

mysql = MySQL(app)

from dbmanager_functions import add_audience,add_director,delete_audience,update_platform,view_directors
from director_functions import *
from audience_functions import *

@app.route('/', methods = ['GET','POST'])
def index():
    return render_template("login.html")

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        cur = mysql.connection.cursor()
        if role == "manager":
            control = cur.execute("SELECT * FROM DB_Managers WHERE username = %s AND password = %s ",[username,password])
            if control > 0:
                cur.close()
                session["username"] = username
                return redirect("/dbmanager")
            else: 
                cur.close()
                return "error"
        elif role == "director":
            control = cur.execute("SELECT * FROM Users u INNER JOIN Directors d ON u.username = d.username WHERE u.username = %s AND u.password = %s ",[username,password])
            if control > 0:
                cur.close()
                session["username"] = username
                return redirect("/director")
            else: 
                cur.close()
                return "error"
        elif role == "audience":
            control = cur.execute("SELECT * FROM Users u INNER JOIN Audiences a ON u.username = a.username WHERE u.username = %s AND u.password = %s ",[username,password])
            if control > 0:
                cur.close()
                session["username"] = username
                return redirect("/audience")
            else: 
                cur.close()
                return "error"    
        cur.close()
    return render_template("index.html")

@app.route('/dbmanager', methods = ['GET','POST'])
def dbmanager():
    return render_template("dbmanager_functions.html")

@app.route('/director', methods = ['GET','POST'])
def get_director():
    return render_template("director_functions.html")

@app.route('/audience', methods = ['GET','POST'])
def get_audience():
    return render_template("audience_functions.html")