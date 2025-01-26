from flask import  Flask,render_template,request
from flask_mysqldb import MySQL
from views import app,mysql

@app.route('/add_audience', methods = ['GET','POST'])
def add_audience():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        surname = request.form.get("surname")

        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO users (username,password,name,surname) VALUES (%s,%s,%s,%s)''', (username,password,name,surname))
        mysql.connection.commit()
        cur.execute("INSERT INTO audiences (username) VALUES (%s)", [username])
        mysql.connection.commit()
        cur.close()

        return render_template("dbmanager_functions.html", message = "user added successfully")
    return render_template("dbmanager_functions.html")

@app.route('/add_director', methods = ['POST'])
def add_director():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        surname = request.form.get("surname")
        nationality = request.form.get("nationality")
        platformid = request.form.get("platformid")

        print("look")
        print(platformid)

        if platformid == "":
            platformid = None
    

        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO users (username,password,name,surname) VALUES (%s,%s,%s,%s)''', (username,password,name,surname))
        mysql.connection.commit()
        cur.execute("INSERT INTO directors (username,nationality) VALUES (%s,%s)", (username,nationality))
        mysql.connection.commit()
        cur.execute("INSERT INTO Director_Platforms (username,platform_id) VALUES (%s,%s)", (username,platformid))
        mysql.connection.commit()
        cur.close()

        return render_template("dbmanager_functions.html", message = "user added successfully")
    return render_template("dbmanager_functions.html")

@app.route('/delete_audience', methods = ['POST'])
def delete_audience():
    if request.method == "POST":
        username = request.form.get("username")

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Audiences WHERE username = %s", [username])
        mysql.connection.commit()
        cur.execute("DELETE FROM Users WHERE username = %s", [username])
        mysql.connection.commit()
        cur.close()

        return render_template("dbmanager_functions.html", message = "user deleted successfully")
    return render_template("dbmanager_functions.html")

@app.route('/update_platform', methods = ['POST'])
def update_platform():
    if request.method == "POST":
        username = request.form.get("username")
        platformid = request.form.get("platformid")

        if platformid == "":
            platformid = None

        cur = mysql.connection.cursor()
        cur.execute("UPDATE Director_Platforms SET platform_id = %s WHERE username = %s", [platformid,username])
        mysql.connection.commit()
        cur.close()

        return render_template("dbmanager_functions.html", message = "director platform updated successfully")
    return render_template("dbmanager_functions.html")

@app.route('/view_directors', methods = ['GET'])
def view_directors():
    if request.method == "GET":

        cur = mysql.connection.cursor()
        control = cur.execute("SELECT Users.username,name,surname,nationality,platform_id FROM Users JOIN Directors ON Directors.username = Users.username JOIN Director_Platforms dp ON dp.username = Users.username")
        if control > 0:
            datas = cur.fetchall()
            cur.close()
            return render_template("show_results.html",directors = datas)

        else:
            cur.close() 
            return render_template("dbmanager_functions.html", message = "couldn't find")
        
    return render_template("dbmanager_functions.html")

@app.route('/view_ratings', methods = ['POST'])
def view_ratings():
    if request.method == "POST":
        username = request.form.get("audience_username")

        cur = mysql.connection.cursor()
        control = cur.execute("SELECT Ratings.movie_id,movie_name,rating FROM Ratings JOIN Movies ON Movies.movie_id = Ratings.movie_id WHERE username = %s ",[username])
        #sakıncalı kontrol et
        if control > 0:
            datas = cur.fetchall()
            cur.close()
            return render_template("show_results.html",ratings = datas)

        else:
            cur.close() 
            return render_template("dbmanager_functions.html", message = "couldn't find")
        
    return render_template("dbmanager_functions.html")

@app.route('/view_director_movies', methods = ['POST'])
def view_director_movies():
    if request.method == "POST":
        username = request.form.get("director_username")
        print(username)
        cur = mysql.connection.cursor()
        control = cur.execute('''
        SELECT m.movie_id, m.movie_name, ms.theatre_id, t.district, ms.time_slot
        FROM Movies m
        JOIN Movie_Sessions ms ON m.movie_id = ms.movie_id
        JOIN Theatres t ON ms.theatre_id = t.theatre_id
        WHERE m.director_username = %s
        ''',[username])
        if control > 0:
            datas = cur.fetchall()
            cur.close()
            return render_template("show_results.html",director_movies = datas)

        else:
            cur.close() 
            return render_template("dbmanager_functions.html", message = "couldn't find")
        
    return render_template("dbmanager_functions.html")

@app.route('/view_movie_rating', methods = ['POST'])
def view_movie_rating():
    if request.method == "POST":
        movie_id = request.form.get("movie_id")
        print(movie_id)

        cur = mysql.connection.cursor()
        control = cur.execute("SELECT movie_id,movie_name,avg_rating FROM Movies WHERE movie_id = %s ",[movie_id])
        if control > 0:
            data = cur.fetchone()
            cur.close()
            return render_template("dbmanager_functions.html",average = data)

        else:
            cur.close() 
            return render_template("dbmanager_functions.html", message = "couldn't find")
        
    return render_template("dbmanager_functions.html")