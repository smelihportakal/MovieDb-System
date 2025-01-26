install all requirements in requirements.txt

pip install -r requirements.txt

change db.yaml according to your mysql database

You can create tables and triggers in query folder and drop them.

Also you can use this script in app folder
creating tables:
python initial.py c

creating triggers:
python initial.py t

droping tables
python initial.py d

Run code in the director /app like python __init__.py

It is important to run __init__py in the app folder.

In my computer:
C:\Courses\CMPE321\Project3\MovieDb-System\app> python __init__.py

after run the code you can see in the terminal a script like:

* Running on http://127.0.0.1:5000
