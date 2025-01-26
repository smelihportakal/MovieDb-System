import mysql.connector
import yaml
import sys

# This code is for creating table and dropping tables. However it is not useful now.
# You must use create_tables.sql and drop_tables.sql files.
 

credits = yaml.safe_load(open('db.yaml'))
db = mysql.connector.connect(
    host= credits["MYSQL_HOST"],
    user = credits["MYSQL_USER"],
    passwd = credits['MYSQL_PASSWORD'],
    database = credits['MYSQL_DB']
)

cursor = db.cursor()

def drop_tables():
    cursor.execute(''' 
        DROP TABLE IF EXISTS Bought_Sessions ; 
        DROP TABLE IF EXISTS Subscribed_Platforms;
        DROP TABLE IF EXISTS Ratings;
        DROP TABLE IF EXISTS Audiences;
        DROP TABLE IF EXISTS Movie_Sessions;
        DROP TABLE IF EXISTS Predecessors;
        DROP TABLE IF EXISTS Movie_Genres; 
        DROP TABLE IF EXISTS Movies;
        DROP TABLE IF EXISTS Director_Platforms;
        DROP TABLE IF EXISTS Directors;
        DROP TABLE IF EXISTS Users;
        DROP TABLE IF EXISTS Rating_Platforms;
        DROP TABLE IF EXISTS Genres;
        DROP TABLE IF EXISTS Theatres;
        DROP TABLE IF EXISTS DB_Managers;
    ''')


def create_tables():  
    cursor.execute('''CREATE TABLE Users (
        username VARCHAR(16) NOT NULL,
        password VARCHAR(16) NOT NULL,
        surname VARCHAR(16),
        name VARCHAR(16),
        PRIMARY KEY (username)
    )''')

    cursor.execute('''CREATE TABLE Audiences (
        username VARCHAR(16) ,
        PRIMARY KEY (username),
        FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE ON UPDATE CASCADE
    )''')

    cursor.execute('''CREATE TABLE Rating_Platforms (
        platform_id INTEGER , 
        platform_name VARCHAR(50),
        PRIMARY KEY (platform_id),
        UNIQUE (platform_name)
    )''')
    

    cursor.execute('''CREATE TABLE Directors (
        username VARCHAR(16) ,
        nationality VARCHAR(50) NOT NULL,
        PRIMARY KEY (username),
        FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE ON UPDATE CASCADE
    )''')

    cursor.execute('''CREATE TABLE Director_Platforms (
        username VARCHAR(16) ,
        platform_id INTEGER,
        PRIMARY KEY (username),
        FOREIGN KEY (username) REFERENCES Directors(username) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (platform_id) REFERENCES Rating_Platforms(platform_id) ON DELETE SET NULL ON UPDATE CASCADE
    )''')    

    cursor.execute('''CREATE TABLE Genres (
        genre_id INTEGER,
        genre_name VARCHAR(50),
        PRIMARY KEY (genre_id),
        UNIQUE (genre_name)
    )''')

    cursor.execute('''CREATE TABLE Theatres (
        theatre_id INTEGER,
        theatre_name VARCHAR(50) NOT NULL,
        capacity INTEGER,
        district VARCHAR(50),
        PRIMARY KEY (theatre_id)
    )''')
    

    cursor.execute('''
    -- a table to store information about movies, including their ID, name, duration, average rating, director, and the platform on which they are rated. The table references the Directors and Rating_Platforms tables via foreign keys.
    CREATE TABLE Movies (
        movie_id INTEGER,
        movie_name VARCHAR(100) NOT NULL,
        duration INTEGER NOT NULL,
        avg_rating REAL,
        director_username VARCHAR(16),
        PRIMARY KEY (movie_id),   
        FOREIGN KEY (director_username) REFERENCES Directors(username) ON DELETE CASCADE ON UPDATE CASCADE
    )''')

    cursor.execute('''
    -- a table to represent movie sessions, which are individual showings of movies at specific theatres. It references the Movies and Theatres tables via foreign keys.
    CREATE TABLE Movie_Sessions (
        session_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        theatre_id INTEGER NOT NULL,
        time_slot INTEGER NOT NULL CHECK (time_slot BETWEEN 1 AND 4),
        date DATE NOT NULL,
        PRIMARY KEY (session_id),
        FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (theatre_id) REFERENCES Theatres(theatre_id) ON DELETE CASCADE ON UPDATE CASCADE
       
    )
    ''')

    cursor.execute('''
    -- a table to store information about database managers, including their username and password.
    CREATE TABLE DB_Managers (
        username VARCHAR(16),
        password VARCHAR(16),
        PRIMARY KEY (username)
    )
    ''')

    

    cursor.execute('''
    -- a table to represent movie sessions that have been bought by members of the audience. It references the Audiences and Movie_Sessions tables via foreign keys.
    CREATE TABLE Bought_Sessions (
        username VARCHAR(16),
        session_id INTEGER,
        PRIMARY KEY (username, session_id),
        FOREIGN KEY (username) REFERENCES Audiences(username) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (session_id) REFERENCES Movie_Sessions(session_id) ON DELETE CASCADE ON UPDATE CASCADE
    )
    ''')

    cursor.execute('''
    -- a table to represent the platforms that members of the audience have subscribed to for rating movies. It references the Audiences and Rating_Platforms tables via foreign keys.
    CREATE TABLE Subscribed_Platforms (
        username VARCHAR(16),
        platform_id INTEGER,
        PRIMARY KEY (username, platform_id),
        FOREIGN KEY (username) REFERENCES Audiences(username) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (platform_id) REFERENCES Rating_Platforms(platform_id) ON DELETE CASCADE ON UPDATE CASCADE
    )
    ''')

    cursor.execute('''
    -- a table to represent the predecessor relationship between movies. It references the Movies table via foreign keys.
    CREATE TABLE Predecessors (
        movie_id INTEGER,
        pmovie_id INTEGER,
        PRIMARY KEY (movie_id, pmovie_id),
        FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (pmovie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE ON UPDATE CASCADE
    )
    ''')

    cursor.execute('''  
    -- a table to represent the relationship between movies and genres. It references the Movies and Genres tables via foreign keys
    CREATE TABLE Movie_Genres (
        movie_id INTEGER,
        genre_id INTEGER,
        PRIMARY KEY (movie_id, genre_id),
        FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE ON UPDATE CASCADE
    )
    ''')
    

    cursor.execute('''
    -- a table to represent ratings given to movies by members of the audience. It references the Audiences and Movies tables via foreign keys.
    CREATE TABLE Ratings (
        username VARCHAR(16),
        movie_id INTEGER,
        rating REAL NOT NULL CHECK (rating BETWEEN 0 AND 5),
        PRIMARY KEY (username, movie_id),
        FOREIGN KEY (username) REFERENCES Audiences(username) ON DELETE CASCADE ON UPDATE CASCADE, 
        FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) ON DELETE CASCADE ON UPDATE CASCADE
        
    )
    ''')

def create_triggers():
    cursor.execute('''
    DROP TRIGGER IF EXISTS BeforeInsertOrUpdateSession;
    CREATE TRIGGER BeforeInsertOrUpdateSession
    BEFORE INSERT ON Movie_Sessions
    FOR EACH ROW
    BEGIN
        DECLARE overlap_count INT;

        SELECT COUNT(*) INTO overlap_count
        FROM Movie_Sessions ms
        INNER JOIN Movies m ON ms.movie_id = m.movie_id
        WHERE session_id <> NEW.session_id
            AND theatre_id = NEW.theatre_id
            AND ms.time_slot <= NEW.time_slot
            AND ms.time_slot + m.duration > NEW.time_slot
            AND date = NEW.date;
            
        IF overlap_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Overlapping sessions not allowed.';
        END IF;
    END;

    DROP TRIGGER IF EXISTS BeforeInsertManager;
    CREATE TRIGGER BeforeInsertManager
    BEFORE INSERT ON DB_Managers
    FOR EACH ROW
    BEGIN  
        DECLARE manager_count INT;
        SELECT COUNT(*) INTO manager_count FROM DB_Managers;
        IF manager_count >= 4 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Maximum limit of 4 database managers reached.';
        END IF;
    END;

    DROP TRIGGER IF EXISTS BeforeInsertRating;
    DROP TRIGGER IF EXISTS AfterInsertRating;
    CREATE TRIGGER BeforeInsertRating
    BEFORE INSERT ON Ratings
    FOR EACH ROW
    BEGIN
        DECLARE user_exists INT;
        DECLARE platform_exists INT;
        DECLARE ticket_exists INT;

        -- Check if the user exists in the Audiences table
        SELECT COUNT(*) INTO user_exists
        FROM Audiences
        WHERE username = NEW.username;

        -- Check if the platform exists in the Subscribed_Platforms table
        SELECT COUNT(*) INTO platform_exists
        FROM Subscribed_Platforms
        WHERE username = NEW.username
        AND platform_id = (
            SELECT dp.platform_id
            FROM Movies m
            JOIN director_platforms dp ON m.director_username = dp.username
            WHERE m.movie_id = NEW.movie_id
        );

        -- Check if the user has bought a ticket for the movie
        SELECT COUNT(*) INTO ticket_exists
        FROM Bought_Sessions bs
        WHERE username = NEW.username
        AND bs.session_id IN (
            SELECT session_id
            FROM Movie_Sessions ms
            WHERE ms.movie_id = NEW.movie_id
        );

        IF user_exists = 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'User does not exist.';
        END IF;
        IF platform_exists = 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'User is not subscribed to the movie platform.';
        END IF;
        IF ticket_exists = 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'User has not bought a ticket for the movie.';
        END IF;
    END;

    CREATE TRIGGER AfterInsertRating
    AFTER INSERT ON Ratings
    FOR EACH ROW
    BEGIN
        -- Update the average rating of the movie
        UPDATE Movies
        SET avg_rating = (
            SELECT AVG(rating)
            FROM Ratings
            WHERE movie_id = NEW.movie_id
        )
        WHERE movie_id = NEW.movie_id;
    END;

    DROP TRIGGER IF EXISTS BeforeInsertBoughtSession;
    CREATE TRIGGER BeforeInsertBoughtSession
    BEFORE INSERT ON Bought_Sessions
    FOR EACH ROW
    BEGIN
        DECLARE predecessors_exist INT;
        DECLARE predecessors_not_watched INT;

        -- Check if the movie has any predecessor movies
        SELECT COUNT(*) INTO predecessors_exist
        FROM Predecessors p
        INNER JOIN movie_sessions ms ON ms.movie_id = p.movie_id
        WHERE ms.session_id = NEW.session_id;

        IF predecessors_exist > 0 THEN
            -- Check if all predecessor movies have been watched
            SELECT COUNT(*) INTO predecessors_not_watched
            FROM Predecessors p
            INNER JOIN movie_sessions ms ON ms.movie_id = p.movie_id
            WHERE ms.session_id = NEW.session_id
            AND p.pmovie_id NOT IN (
                SELECT ms.movie_id
                FROM Bought_Sessions bs
                JOIN movie_sessions ms ON bs.session_id = ms.session_id
                WHERE bs.username = NEW.username
            );

            IF predecessors_not_watched > 0 THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'All predecessor movies must be watched in order to buy a ticket for this movie session.';
            END IF;
        END IF;
    END;
    ''')



def insert():
    cursor.execute('''INSERT INTO DB_Managers (username, password)
    VALUES ('manager1', 'managerpass1'),
       ('manager2', 'managerpass2'),
       ('manager35', 'managerpass35');
    ''')

    cursor.execute('''INSERT INTO genres (genre_id, genre_name)
    VALUES (80001, 'Animation'),
       (80002, 'Comedy'),
       (80003, 'Adventure'),
       (80004, 'Real Story'),
       (80005, 'Thriller'),
       (80006, 'Drama');
    ''')

    cursor.execute('''INSERT INTO rating_platforms (platform_id, platform_name)
    VALUES (10130, 'IMDB'),
       (10131, 'Letterboxd'),
       (10132, 'FilmIzle'),
       (10133, 'Filmora'),
       (10134, 'BollywoodMDB');
    ''')

    cursor.execute('''INSERT INTO Users (username, password, surname, name)
    VALUES
        ('steven.jobs', 'apple123', 'Jobs', 'Steven'),
        ('minion.lover', 'bello387', 'Gru', 'Felonius'),
        ('steve.wozniak', 'pass4321', 'Andrews', 'Ryan'),
        ('he.gongmin', 'passwordpass', 'Gongmin', 'He'),
        ('carm.galian', 'madrid9897', 'Galiano', 'Carmelita'),
        ('kron.helene', 'helenepass', 'Kron', 'Helene'),
        ('arzucan.ozgur', 'deneme123', 'Ozgur', 'Arzucan'),
        ('egemen.isguder', 'deneme124', 'Isguder', 'Egemen'),
        ('busra.oguzoglu', 'deneme125', 'Oguzoglu', 'Busra'),
        ('peter.weir', 'peter weir879', 'Weir', 'Peter'),
        ('kyle.balda', 'mynameiskyle9', 'Balda', 'Kyle');
    ''')

    cursor.execute('''
    -- Insert data into the Audiences table
    INSERT INTO Audiences (username)
    VALUES
        ('steven.jobs'),
        ('steve.wozniak'),
        ('arzucan.ozgur'),
        ('egemen.isguder'),
        ('busra.oguzoglu');
    ''')

    cursor.execute('''
    -- Insert data into the Directors table
    INSERT INTO Directors (username, nationality)
    VALUES
        ('he.gongmin', 'Turkish'),
        ('carm.galian', 'Turkish'),
        ('kron.helene', 'French'),
        ('peter.weir', 'Spanish'),
        ('kyle.balda', 'German');
    ''')

    cursor.execute('''
    -- Insert data into the Director_Platforms table
    INSERT INTO Director_Platforms (username, platform_id)
    VALUES
        ('he.gongmin', 10130),
        ('carm.galian', 10131),
        ('kron.helene', 10130),
        ('peter.weir', 10131),
        ('kyle.balda', 10132);
    ''')


    cursor.execute('''
    -- Insert data into the Theatres table
    INSERT INTO Theatres (theatre_id, theatre_name, capacity, district)
    VALUES
        (40001, 'Sisli 1', 300, 'Sisli'),
        (40002, 'Sisli 2', 200, 'Sisli'),
        (40003, 'Besiktas1', 100, 'Besiktas'),
        (40004, 'Besiktas2', 100, 'Besiktas'),
        (40005, 'Besiktas3', 500, 'Besiktas');
    ''')

    cursor.execute('''
    -- Insert data into the Movies table
    INSERT INTO Movies (movie_id, movie_name, duration, avg_rating, director_username)
    VALUES
        (20001, 'Despicable Me', 2, 5, 'kyle.balda'),
        (20002, 'Catch Me If You Can', 2, NULL, 'he.gongmin'),
        (20003, 'The Bone Collector', 2, NULL, 'carm.galian'),
        (20004, 'Eagle Eye', 2, 5, 'kron.helene'),
        (20005, 'Minions: The Rise Of Gru', 1, 5, 'kyle.balda'),
        (20006, 'The Minions', 1, 5, 'kyle.balda'),
        (20007, 'The Truman Show', 3, 5, 'peter.weir');
    ''')

    cursor.execute('''
    -- Insert data into the Movie_Sessions table
    INSERT INTO Movie_Sessions (session_id, movie_id, theatre_id, time_slot, date)
    VALUES
        (50001, 20001, 40001, 1, '2023-03-15'),
        (50002, 20001, 40001, 3, '2023-03-15'),
        (50003, 20001, 40002, 1, '2023-03-15'),
        (50004, 20002, 40002, 3, '2023-03-15'),
        (50005, 20003, 40003, 1, '2023-03-16'),
        (50006, 20004, 40003, 3, '2023-03-16'),
        (50007, 20005, 40004, 1, '2023-03-16'),
        (50008, 20006, 40004, 3, '2023-03-16'),
        (50009, 20007, 40005, 1, '2023-03-16');
    ''')

    cursor.execute('''
    -- Insert data into the Bought_Sessions table
    INSERT INTO Bought_Sessions (username, session_id)
    VALUES
        ('steven.jobs', 50001),
        ('steve.wozniak', 50004),
        ('steve.wozniak', 50005),
        ('arzucan.ozgur', 50006),
        ('egemen.isguder', 50008),
        ('egemen.isguder', 50004),
        ('egemen.isguder', 50007),
        ('egemen.isguder', 50001),
        ('busra.oguzoglu', 50009);
    ''')

    cursor.execute('''
    -- Insert data into the Subscribed_Platforms table
    INSERT INTO Subscribed_Platforms (username, platform_id)
    VALUES
        ('steven.jobs', 10130),
        ('steven.jobs', 10131),
        ('steve.wozniak', 10131),
        ('arzucan.ozgur', 10130),
        ('egemen.isguder', 10132),
        ('busra.oguzoglu', 10131);
    ''')

    cursor.execute('''
    -- Insert data into the Predecessors table
    INSERT INTO Predecessors (movie_id, pmovie_id)
    VALUES
        (20005, 20006),
        (20005, 20001),
        (20006, 20001);
    ''')

    cursor.execute('''
    -- Insert data into the Movie_Genres table
    INSERT INTO Movie_Genres (movie_id, genre_id)
    VALUES
        (20001, 80001),
        (20001, 80002),
        (20002, 80003),
        (20002, 80004),
        (20003, 80005),
        (20004, 80003),
        (20005, 80001),
        (20005, 80002),
        (20006, 80001),
        (20006, 80002),
        (20007, 80002),
        (20007, 80006);
    ''')

    cursor.execute('''
    -- Insert data into the Ratings table
    INSERT INTO Ratings (username, movie_id, rating)
    VALUES
        ('egemen.isguder', 20001, 5),
        ('egemen.isguder', 20005, 5),
        ('egemen.isguder', 20006, 5),
        ('arzucan.ozgur', 20004, 5),
        ('busra.oguzoglu', 20007, 5);
    ''')


    db.commit()


arg = sys.argv[1]

if arg == 'd':
    drop_tables()
elif arg == 'c':
    create_tables()
elif arg == 'i':
    insert()
elif arg == 't':
    create_triggers()