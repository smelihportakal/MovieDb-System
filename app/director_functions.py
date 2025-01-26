from flask import  Flask,render_template,request,session
from flask_mysqldb import MySQL
from views import app,mysql

@app.route('/list_theatres', methods = ['POST'])
def list_theatres():
    if request.method == "POST":
        date = request.form.get("date")
        time_slot = request.form.get("time_slot")
        
        cur = mysql.connection.cursor()
        control = cur.execute(''' 
        SELECT t.theatre_id, t.district, t.capacity
        FROM Theatres t  
        WHERE t.theatre_id NOT IN (
            SELECT ms.theatre_id
            FROM Movie_Sessions ms
            INNER JOIN Movies m ON ms.movie_id = m.movie_id
            WHERE ms.time_slot <= %s
            AND ms.date = %s
            AND (ms.time_slot + m.duration) > %s
        )
        ''', [time_slot,date,time_slot])

        if control > 0:
            datas = cur.fetchall()
            cur.close()
            return render_template("show_results.html",theatres = datas)

        else:
            cur.close() 
            return render_template("director_functions.html", message = "Could not find")
        
    return render_template("director_functions.html")

# add_movie,add_movie_session,add_predecessor
@app.route('/add_movie', methods = ['POST'])
def add_movie():
    if request.method == "POST":
        movie_id = request.form.get("movie_id")
        movie_name = request.form.get("movie_name")
        duration = request.form.get("duration")
        genres = request.form.get("genres")
        avg_rating = None
        username = session["username"]

        if genres == "":
            return render_template("director_functions.html", message = "genre cannot be empty")

        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO Movies (movie_id,movie_name,duration,avg_rating,director_username) VALUES (%s,%s,%s,%s,%s)''', (movie_id,movie_name,duration,avg_rating,username))
        mysql.connection.commit()

        genre_list = genres.split(",")
        for genre_id in genre_list:
            cur.execute('''INSERT INTO Movie_Genres (movie_id,genre_id) VALUES (%s,%s)''', (movie_id,genre_id))
            mysql.connection.commit()

        cur.close()

        return render_template("director_functions.html", message = "movie added successfully")
    return render_template("director_functions.html")

@app.route('/add_movie_session', methods = ['POST'])
def add_movie_session():
    if request.method == "POST":
        session_id = request.form.get("session_id")
        movie_id = request.form.get("movie_id")
        theatre_id = request.form.get("theatre_id")
        time_slot = request.form.get("time_slot")
        date = request.form.get("date")

        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO Movie_Sessions (session_id,movie_id,theatre_id,time_slot,date) VALUES (%s,%s,%s,%s,%s)''', (session_id,movie_id,theatre_id,time_slot,date))
        mysql.connection.commit()

        cur.close()

        return render_template("director_functions.html", message = "movie session added successfully")
    return render_template("director_functions.html")

@app.route('/add_theatre', methods = ['POST'])
def add_theatre():
    if request.method == "POST":
        theatre_id = request.form.get("theatre_id")
        theatre_name = request.form.get("theatre_name")
        capacity = request.form.get("theatre_capacity")
        district = request.form.get("district")

        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO Theatres (theatre_id,theatre_name,capacity,district) VALUES (%s,%s,%s,%s)''', (theatre_id,theatre_name,capacity,district))
        mysql.connection.commit()

        cur.close()

        return render_template("director_functions.html", message = "theatre added successfully")
    return render_template("director_functions.html")

@app.route('/add_predecessor', methods = ['POST'])
def add_predecessor():
    if request.method == "POST":
        movie_id = request.form.get("movie_id")
        predecessors = request.form.get("predecessors")

        cur = mysql.connection.cursor()

        if predecessors != "":
            predecessor_list = predecessors.split(",")
            for pmovie_id in predecessor_list:
                cur.execute('''INSERT INTO Predecessors (movie_id,pmovie_id) VALUES (%s,%s)''', (movie_id,pmovie_id))
                mysql.connection.commit()

        cur.close()

        return render_template("director_functions.html", message = "movie predecessors added successfully")
    return render_template("director_functions.html")

@app.route('/view_directed_movies', methods = ['GET'])
def view_directed_movies():
    if request.method == "GET":
        username = session['username']

        cur = mysql.connection.cursor()
        control = cur.execute(''' 
        SELECT m.movie_id, m.movie_name, ms.theatre_id, ms.time_slot, 
            GROUP_CONCAT(p.pmovie_id) AS predecessors_list
        FROM Movies m
        JOIN Movie_Sessions ms ON m.movie_id = ms.movie_id
        LEFT JOIN Predecessors p ON m.movie_id = p.movie_id
        WHERE m.director_username = %s
        GROUP BY m.movie_id, m.movie_name, ms.theatre_id, ms.time_slot
        ORDER BY m.movie_id ASC;
        ''', [username])

        if control > 0:
            datas = cur.fetchall()

            """

            for movie in datas:
                movie = list(movie)
                movie_id = movie[0]
                c = cur.execute(''' 
                    SELECT pmovie_id
                    FROM Predecessors
                    WHERE movie_id = %s
                    ''', [movie_id])
                predecessor_str = ""
                if c > 0:
                    pmovies = cur.fetchall()
                    predecessor_str += str(pmovies[0][0])

                    for i in range(1,len(pmovies)):
                        predecessor_str += "," + str(pmovies[i][0])
                
                movie.append(predecessor_str)

            """
                

            cur.close()
            return render_template("show_results.html",movies_directed = datas)

        else:
            cur.close() 
            return render_template("director_functions.html", message = "Could not find")
        
    return render_template("director_functions.html")

@app.route('/view_movie_audiences', methods = ['POST'])
def view_movie_audiences():
    if request.method == "POST":
        movie_id = request.form.get("movie_id")
        username = session["username"]

        cur = mysql.connection.cursor()
        control = cur.execute(''' 
        SELECT a.username, u.name, u.surname
        FROM Audiences a
        JOIN Bought_Sessions bs ON a.username = bs.username
        JOIN Movie_Sessions ms ON bs.session_id = ms.session_id
        JOIN Movies m ON ms.movie_id = m.movie_id
        JOIN Users u ON a.username = u.username
        WHERE m.movie_id = %s AND m.director_username = %s
        ''', [movie_id,username])

        if control > 0:
            datas = cur.fetchall()
            cur.close()
            return render_template("show_results.html",audiences = datas)

        else:
            cur.close() 
            return render_template("director_functions.html", message = "Could not find")
        
    return render_template("director_functions.html")

@app.route('/update_movie_name', methods = ['POST'])
def update_movie_name():
    if request.method == "POST":
        movie_id = request.form.get("movie_id")
        movie_name = request.form.get("movie_name")
        username = session["username"]

        cur = mysql.connection.cursor()
        cur.execute("UPDATE Movies SET movie_name = %s WHERE movie_id = %s AND director_username = %s", [movie_name,movie_id,username])
        mysql.connection.commit()
        cur.close()

        return render_template("director_functions.html", message = "movie name updated")
    return render_template("director_functions.html")