"""main function """

import datetime

from dbconfig import DB
from flask import Flask, render_template, url_for,  request, redirect, session
import sqlite3



app = Flask(__name__)

app.secret_key = 'dffg67789@#$%^&*iuyt@'

def insert_list_data(mlist):
    connection = sqlite3.connect("jjed.db")
    cursor = connection.cursor()
    try:
        sql = """ INSERT INTO interns(intern_name, intern_school,intern_level,intern_contact,intern_email)VALUES(?,?,?,?,?)"""
        cursor.executemany(sql, mlist)
        connection.commit()
        print("commited")
    except connection.Error as error:
        print(error)
    finally:
        connection.close()

intern = [("Mary Dufie Afrane", "University of Cape Coast", "Level 300", "0558027244", "maryakua3@gmail.com"),
         ("Joshua Nyarko Boateng", "Accra Technical University", "Level 200", "0245553697", "joshua.goat19@gmail.com"),
          ("Enoch Sem", "University of Cape Coast", "Level 300", "0569775844", "enochsem@gmail.com"),
          ("jojo Sem", "University of Cape k", "Level 300", "0569765844", "jojosem@gmail.com"),
          ("Jojo ", "Ashesi University", "Level 300", "0558027244", "jojo@gmail.com")

           ]
# insert_list_data(intern)

def update_db():
    pass
# form_data = request.form()
# insert_list_data(form_data)

@app.route("/", methods=["POST","GET"])
def index():
    response = None
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        session['username'] = name
        db = DB()
        response = db.authentication("interns", "intern_name", name, "intern_email", email)
        if response == True:
            return redirect(url_for('intern_home'))
    return render_template("intern_login.html", error = response)


# @app.route("/", methods=["POST"])
# def auth():
#     response = ""
#     if request.method == "POST":
#         name = request.form["name"]
#         email = request.form["email"]
#         # connection = sqlite3.connect("jjed.db")
#         # cursor = connection.cursor()
#         # cursor.execute("SELECT * FROM interns WHERE intern_name=?", (name,))
#         # if cursor.fetchall():
#         #     return redirect(url_for('intern_home'))
#         db = DB()
#         response = db.authentication("interns", "intern_name", name, "intern_email", email)
#         if response == True:
#             return redirect(url_for('intern_home'))
#         else:
#             return redirect(url_for('index'))
#     return render_template("intern_login.html" , error = response)
   



@app.route("/admin_home", methods=["POST","GET"])
def admin_home():
    if not session.get("username"):
        return redirect(url_for("index"))
    
    db = DB()
    activities = db.select_all("activities")
    lenght = len(activities)

    interns = db.select_all("interns")
    lenght_interns = len(interns)
    
    #creating and inserting activities
    if request.method == "POST":
        if request.form['submit'] == 'Create activity':
            # title = request.form["title"][0 : -1]
            title = request.form.get("title")
            content = request.form.get("content")
            db.insert("activities","activity_title","activity_content", title, content)
            return redirect(url_for("admin_home"))

        # delete activity
        if request.form["submit"] == "Delete":
            delete_id = request.form["delete_id"]
            db.delete_one("activities", delete_id)
            return redirect(url_for("admin_home"))

        if request.form["submit"] == "Add Student":
            username = request.form["username"]
            contact= request.form["contact"]
            email = request.form["email"]
            school = request.form["school"]
            level = request.form.get("level")
            db.insert_intern("interns", username, school, level, contact, email)
            return redirect(url_for("admin_home"))
        

    
    return render_template("admin_home.html", activities = activities, lenght=lenght, interns =interns, lenght_interns=lenght_interns)


@app.route("/admin_home/<edit_id>", methods=["POST","GET"])
def admin(edit_id):
    edit_activity = None
    if request.method == "POST":
        db = DB()
        edit_activity = db.select_all("activities")
        # edit_length = len(edit_activity)
    return edit_activity


# @app.route("/admin_home/delete_row",methods=["POST","GET"])
# def action():
#     if request.method =="POST":
#         db =DB()
#         delete_id = request.form["delete_id"]
#         db.delete("activities", activity_id, delete_id)
#         return redirect(url_for("admin_home"))


@app.route("/admin_login", methods=["POST","GET"])
def admin_login():
    if request.method == "POST":
        name = request.form["name"]
        session["username"] = name
        password = request.form["password"]
        connection = sqlite3.connect("jjed.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM admins WHERE admin_name=? AND admin_password=?", (name,password,))
        row = cursor.fetchall()
        if row:
            return redirect(url_for('admin_home'))
        else:
            return redirect(url_for('admin_login'))

    return render_template("admin_login.html")



@app.route("/intern_home", methods = ['POST','GET'])
def intern_home():
    if not session.get("username"):
        return redirect(url_for("index"))

    isChecked=False
    if request.method == "POST":
        global intern_name
        global current_date_time
        isChecked = request.form['checked']
        intern_name = session.get("username")
        current_date_time = datetime.datetime.now()
        
        connection = sqlite3.connect("jjed.db")
        cursor = connection.cursor()
        try:
            sql = """ INSERT INTO attendance(intern_name,attendance_datetime)VALUES(?,?)"""
            cursor.execute(sql,[intern_name,current_date_time])
            connection.commit()
            print("inserted")
        except connection.Error as error:
            print(error)
        finally:
            connection.close()


    connection = sqlite3.connect("jjed.db")
    cursor = connection.cursor()
    
    activity_query = """SELECT * FROM activities WHERE activity_title ='Activity'  """
    lab_link_query = """SELECT * FROM activities WHERE activity_title ='Lab link'  """
    zoom_link_query = """SELECT * FROM activities WHERE activity_title ='Zoom Link'  """
    quick_query = """SELECT * FROM activities WHERE activity_title ='Quick Notes'  """
    
    cursor.execute(activity_query)
    activities = cursor.fetchall()
    
    cursor.execute(lab_link_query)
    lab_links = cursor.fetchall()
    
    cursor.execute(zoom_link_query)
    zoom_links = cursor.fetchall()
    
    cursor.execute(quick_query)
    quick_notes = cursor.fetchall()
    
    connection.close()
    
    return render_template("intern_home.html", isChecked=True if isChecked=='on' else False, activities = activities, lab_links = lab_links, zoom_links = zoom_links, quick_notes= quick_notes)



@app.route("/logout")
def logout():
    session["username"] = None
    # or
    session.pop('username', default=None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

