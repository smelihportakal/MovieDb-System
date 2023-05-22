from flask import  Flask,render_template,request
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)

db = yaml.safe_load(open('db.yaml'))
app.config["MYSQL_HOST"] = db["MYSQL_HOST"] 
app.config["MYSQL_USER"] = db["MYSQL_USER"]
app.config['MYSQL_PASSWORD'] = db['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = db['MYSQL_DB']

mysql = MySQL(app)

@app.route('/', methods = ['GET','POST'])
def index():
    
    return render_template("index.html")

@app.route('/add_user', methods = ['GET','POST'])
def add_user():
    return render_template("add_user.html")

@app.route('/director_functions', methods = ['GET','POST'])
def get_director_functions():
    return render_template("director_functions.html")

@app.route('/audience_functions', methods = ['GET','POST'])
def get_audience_functions():
    return render_template("audience_functions.html")

if __name__ == "__main__":
    
    app.run(debug=True)