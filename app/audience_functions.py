from flask import  Flask,render_template,request,session
from flask_mysqldb import MySQL
from views import app,mysql

@app.route('/list_movies', methods = ['GET'])
def list_movies():
    if request.method == "GET":
        
        cur = mysql.connection.cursor()
        control = cur.execute(''' 
        SELECT m.movie_id, m.movie_name, u.surname, rp.platform_name, ms.theatre_id, ms.time_slot, GROUP_CONCAT(p.pmovie_id)
        FROM Movies m
        JOIN Director_Platforms dp ON  m.director_username = dp.username
        JOIN Rating_Platforms rp ON dp.platform_id = rp.platform_id
        JOIN Movie_Sessions ms ON m.movie_id = ms.movie_id
        JOIN Users u ON m.director_username = u.username
        LEFT JOIN Predecessors p ON m.movie_id = p.movie_id
        GROUP BY m.movie_id, ms.theatre_id, ms.time_slot
        ORDER BY m.movie_id;
        ''')

        if control > 0:
            datas = cur.fetchall()
            cur.close()
            return render_template("show_results.html",movies = datas)

        else:
            cur.close() 
            return render_template("audience_functions.html", message = "Could not find")
        
    return render_template("audience_functions.html")

@app.route('/buy_ticket', methods = ['POST'])
def buy_ticket():
    if request.method == "POST":
        session_id = request.form.get("session_id")
        username = session["username"]

        cur = mysql.connection.cursor()

        cur.execute('SELECT movie_id,date,time_slot FROM Movie_Sessions WHERE session_id = %s', [session_id])
        result = cur.fetchone()
        if result is None:
            return render_template("audience_functions.html", message = "Invalid session ID")

        movie_id = result[0]
        date = result[1]
        time_slot = result[2]

        cur.execute('SELECT pmovie_id FROM Predecessors WHERE movie_id = %s', [movie_id])
        predecessors = [row[0] for row in cur.fetchall()]

        for predecessor in predecessors:
            cur.execute('''
            SELECT bs.session_id 
            FROM Bought_Sessions bs
            JOIN Movie_Sessions ms ON bs.session_id = ms.session_id
            JOIN Movies m ON ms.movie_id = m.movie_id
            WHERE bs.username = %s AND ms.movie_id = %s AND ( ms.date < %s OR (ms.time_slot + m.duration <= %s AND ms.date = %s))
            ''', (username, predecessor, date, time_slot, date))
            result = cur.fetchone()
            if result is None:
                return render_template("audience_functions.html", message = "You need to watch the predecessor movie(s) first")

        
        cur.execute('SELECT COUNT(*) FROM Bought_Sessions WHERE session_id = %s', [session_id])
        result = cur.fetchone()
        if result is not None:
            bought_count = result[0]

            cur.execute('SELECT capacity FROM Theatres JOIN Movie_Sessions ON Theatres.theatre_id = Movie_Sessions.theatre_id WHERE session_id = %s', [session_id])
            capacity = cur.fetchone()[0]

            if bought_count >= capacity:
                return render_template("audience_functions.html", message = "The theater is full, cannot buy a ticket")

        
        cur.execute('INSERT INTO Bought_Sessions (username, session_id) VALUES (%s, %s)', (username, session_id))
        mysql.connection.commit()
        cur.close()

        return render_template("audience_functions.html", message = "Ticket purchased successfully")
    return render_template("audience_functions.html")

@app.route('/view_tickets', methods = ['GET'])
def view_tickets():
    if request.method == "GET":
        username = session["username"]
        
        cur = mysql.connection.cursor()
        control = cur.execute(''' 
        SELECT m.movie_id, m.movie_name, ms.session_id, r.rating, m.avg_rating
        FROM Bought_Sessions bs
        JOIN Movie_Sessions ms ON bs.session_id = ms.session_id
        JOIN Movies m ON ms.movie_id = m.movie_id
        LEFT JOIN Ratings r ON ms.movie_id = r.movie_id AND bs.username = r.username
        WHERE bs.username = %s
        ''',[username])

        if control > 0:
            datas = cur.fetchall()
            cur.close()
            return render_template("show_results.html",tickets = datas)

        else:
            cur.close() 
            return render_template("audience_functions.html", message = "Could not find")
        
    return render_template("audience_functions.html")