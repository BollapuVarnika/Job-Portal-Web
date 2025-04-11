from flask import *
import sqlite3

app=Flask(__name__)
def create_tables():
    with sqlite3.connect("SQL/Registration.db") as conn:
        c = conn.cursor()
        # Creating Registration Table
        c.execute("""CREATE TABLE IF NOT EXISTS Registration(
                        fname TEXT,
                        lname TEXT,
                        age INTEGER,
                        email TEXT NOT NULL UNIQUE,
                        phone TEXT)
                """)
        # Creating Jobs Table
        c.execute("""CREATE TABLE IF NOT EXISTS Jobs(
                        Title TEXT,
                        Description TEXT,
                        Location TEXT,
                        Salary INTEGER)
                """)
        c.execute("""CREATE TABLE IF NOT EXISTS Applications (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT,
                    User_email TEXT,
                    Cover_letter TEXT,
                    FOREIGN KEY (Title) REFERENCES Jobs (Title),
                    FOREIGN KEY (User_email) REFERENCES Registration (email))""")

        conn.commit()

# Run table creation before the first request

def setup():
    create_tables()

setup()

# RUNNING HOME PAGE OF JOB PORTAL

@app.route("/")
def homePage():
    return render_template("index.html")

#REGISTRATION PAGE

@app.route("/register")
def run_register():
    return render_template("register.html")

#INSERTING USER DETAILS INTO REGISTRATION TABLE

def insert_user(fname,lname,age,email,phone):
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    c.execute("INSERT INTO Registration(fname,lname,age,email,phone)VALUES(?,?,?,?,?)",(fname,lname,age,email,phone))
    conn.commit()
    conn.close()

# CHECKING THE REGISTRATION TO AVOID DUPLICATES

def check_user(email):
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    c.execute("SELECT email FROM Registration WHERE email=?",(email,))
    result=c.fetchone()
    return result is not None

#REGISTRATION FROM

@app.route("/register", methods=["POST"])
def register():
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    phone = request.form.get("phone")
    age = request.form.get("age")
    pwd = request.form.get("password")
    confirm = request.form.get("confirm_password")

    if fname.isalpha() and lname.isalpha():
        if pwd == confirm:
            try:
                if not check_user(email):
                    insert_user(fname, lname, age, email, phone)
                    return "Registered"
                else:
                    return "Error: Email already registered."
            except sqlite3.IntegrityError:
                return "Error: Email already registered."
        else:
            return "Error: Passwords do not match."
    return "Error: Invalid input."


# SEARCHINNG JOBS

@app.route("/search")
def search():
    return render_template("search_jobs.html")


@app.route("/search_job",methods=["POST"])
def search_job():
    title=request.form.get("title")
    location=request.form.get("location")
    salary=request.form.get("salary")
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    if(title!=None and location!=None and salary!=None):
         c.execute("SELECT * FROM Jobs WHERE Title=? AND Salary=? AND Location=?",(title,salary,location))
         jobs=c.fetchall()
    elif(location==None):
        c.execute("SELECT * FROM Jobs WHERE Title=? AND Salary=?",(title,salary))
        jobs=c.fetchall()
    elif(salary==None):
         c.execute("SELECT * FROM Jobs WHERE Title=? AND Location=?",(title,location))
         jobs=c.fetchall()
    elif(title==None):
         c.execute("SELECT * FROM Jobs WHERE Location=? AND Salary=?",(location,salary))
         jobs=c.fetchall()
    elif(title!=None):
        c.execute("SELECT * FROM Jobs WHERE Title=?",(title,))
        jobs=c.fetchall()
    elif(location!=None):
        c.execute("SELECT * FROM Jobs WHERE Location=?",(location,))
        jobs=c.fetchall()
    elif(salary!=None):
        c.execute("SELECT * FROM Jobs WHERE Salary=?",(salary,))
        jobs=c.fetchall()
    else:
        return "Error:No data is avaliable"
    conn.commit()
    conn.close()
    return render_template("listing.html",jobs=jobs)



@app.route("/apply_job")
def apply_job():
    return render_template("apply.html")

@app.route("/apply", methods=["POST"])
def apply():
    title=request.form.get("title")
    email = request.form.get("email")
    cover_letter = request.form.get("cover_letter")
    conn = sqlite3.connect("SQL/Registration.db")
    c = conn.cursor()
    c.execute('SELECT Title FROM Jobs WHERE Title=?',(title,))
    t=c.fetchone()
    if not t:
        return "Error:No data is avaliable"
    # Check if the user exists
    c.execute("SELECT email FROM Registration WHERE email=?", (email,))
    user = c.fetchone()
    if not user:
        return redirect(url_for("register"))
    c.execute("INSERT INTO Applications(Title,User_email,Cover_letter)VALUES(?,?,?)",(title,email,cover_letter))
    conn.commit()
    conn.close()
    return "Application submitted succesfully"

#ADDING NEW JOB POSTS 

@app.route("/posting")
def run_posting():
    return render_template("jobPosting.html")

def insert_jobposting(role,des,location,salary):
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    c.execute("INSERT INTO Jobs(Title,Description,Location,Salary)VALUES(?,?,?,?)",(role,des,location,salary))
    conn.commit()
    conn.close()


@app.route("/posting",methods=["POST"])
def posting():
    role=request.form.get("Role")
    description=request.form.get("description")
    location=request.form.get("location")
    salary=request.form.get("salary")
    insert_jobposting(role,description,location,salary)
    return listing()

#LISTING THE ALL JOB POSTS

@app.route("/listing")
def listing():
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    c.execute("SELECT * FROM Jobs")
    jobs=c.fetchall()
    conn.commit()
    conn.close()
    return render_template("listing.html", jobs=jobs)

# MANAGE JOBS

@app.route("/manage_jobs")
def manage_jobs():
    return render_template("manage_jobs.html")

#UPDATING JOB LISTING

@app.route("/update_job",methods=["POST"])
def update_job():
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    title=request.form.get("title")
    location=request.form.get("location")
    description=request.form.get("description")
    salary=request.form.get("salary")
    if(location!="None"):
        c.execute("UPDATE JOBS SET Location=? WHERE Title=?",(location,title))
    if(description!="None"):
        c.execute("UPDATE JOBS SET Description=? WHERE Title=?",(description,title))
    if(salary!="None"):
        c.execute("UPDATE JOBS SET Salary=? WHERE Title=?",(salary,title))
    conn.commit()
    conn.close()
    return listing()

@app.route("/jobs")
def jobs():
    return render_template("update_job.html")

# DELETING JOB POSTING

@app.route("/delete_job",methods=["POST"])
def delete():
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    title=request.form.get("title")
    c.execute("DELETE FROM Jobs where Title=?",(title,))
    conn.commit()
    conn.close()
    return listing()

@app.route("/delete_job")
def delete_job():
    return render_template("delete_job.html")

@app.route("/manage_application")
def application():
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    c.execute("SELECT * FROM Applications")
    application=c.fetchall()
    conn.commit()
    conn.close()
    return render_template("applications.html",applications=application)

# MANAGE USER

@app.route("/manage_user")
def manage_user():
    return render_template("manage_users.html")

@app.route("/add_user")
def add_user():
    return render_template("register.html")

# UPDATING USER DETAILS

@app.route("/change_user")
def change_user():
    return render_template("update_user.html")

@app.route("/update_user",methods=["POST"])
def update_user():
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    gmail=request.form.get("gmail")
    fname=request.form.get("fname")
    lname=request.form.get("lname")
    phone=request.form.get("phone")
    age=request.form.get("age")
    email=request.form.get("email")
    if(fname!="None"):
        c.execute("UPDATE Registration SET fname=? WHERE email=?",(fname,gmail))
    if(lname!="None"):
        c.execute("UPDATE Registration SET lname=? WHERE email=?",(lname,gmail))
    if(phone!="None"):
        c.execute("UPDATE Registration SET phone=? WHERE email=?",(phone,gmail))
    if(age!="None"):
        c.execute("UPDATE Registration SET age=? WHERE email=?",(age,gmail))
    if(email!="None"):
        c.execute("UPDATE Registration SET email=? WHERE email=?",(email,gmail))
    conn.commit()
    conn.close()
    return "Updated Successfully"

# DELETING USER DETAILS

@app.route("/delete_users",methods=["POST"])
def delete_users():
    conn=sqlite3.connect("SQL/Registration.db")
    c=conn.cursor()
    email=request.form.get("email")
    c.execute("DELETE FROM Registration where email=?",(email,))
    conn.commit()
    conn.close()
    return "Deleted Successfully"

@app.route("/delete_user")
def delete_user():
    return render_template("delete_user.html")


if __name__=='__main__':
    app.run(debug=True)