import os, re
from flask import Flask 
from flask import render_template, request, url_for,redirect, session, abort, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
from werkzeug.utils import secure_filename
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


curr_dir=os.path.abspath(os.path.dirname(__file__))

#Creating a Flask instance
app=Flask(__name__, template_folder="templates")
app.secret_key="21f1003052"


#adding the database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(curr_dir,'booktheshow.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

#setting uploading types of images & the folder to upload images
app.config['UPLOAD_EXTENSIONS']=['.jpg', '.png', '.jpeg']
app.config['UPLOAD_PATH']=os.path.join(curr_dir, 'static', 'img')


from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()


class Admin(db.Model):
    __tablename__="admin"
    admin_id=db.Column(db.Integer, primary_key=True, nullable=False)
    ad_fname=db.Column(db.String(30), nullable=False)
    ad_lname=db.Column(db.String(30))
    ad_email=db.Column(db.String(30), nullable=False)
    ad_username=db.Column(db.String(20), nullable=False, unique=True)
    ad_pwd=db.Column(db.String(20), nullable=False)
    ad_loc=db.Column(db.String(20), nullable=False)
    ad_img=db.Column(db.String(50), nullable=False)

class Bookings(db.Model):
    __tablename__="bookings"
    booking_id=db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    booking_date_time=db.Column(db.String(30), nullable=False)
    buser_id=db.Column(db.Integer, nullable=False)
    bshow_id=db.Column(db.Integer, nullable=False)
    bvenue_id=db.Column(db.Integer, nullable=False)


class Shows(db.Model):
    __tablename__="shows"
    show_id=db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    show_name=db.Column(db.String(30), nullable=False)
    show_rating=db.Column(db.Numeric(precision=2, scale=1), nullable=False)
    show_time=db.Column(db.String(40), nullable=False)
    show_date=db.Column(db.String(40), nullable=False)
    show_tag=db.Column(db.String(30), nullable=False)
    show_price=db.Column(db.Integer, nullable=False)
    show_image=db.Column(db.String(50), nullable=False)
    show_capacity=db.Column(db.Integer, nullable=False)
    show_venue_id=db.Column(db.Integer, nullable=False)
    show_admin_id=db.Column(db.Integer, nullable=False)
    show_revenue=db.Column(db.Integer, nullable=False)

class Users(db.Model):
    __tablename__="users"
    user_id=db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_fname=db.Column(db.String(30), nullable=False)
    user_lname=db.Column(db.String(30))
    user_email=db.Column(db.String(30), nullable=False)
    user_username=db.Column(db.String(20), nullable=False, unique=True)
    user_pwd=db.Column(db.String(20), nullable=False)
    user_loc=db.Column(db.String(20), nullable=False)
    user_img=db.Column(db.String(50), nullable=False)

class Venue(db.Model):
    __tablename__="venue"
    venue_id=db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    venue_name=db.Column(db.String(30), nullable=False)
    venue_location=db.Column(db.String(30), nullable=False)
    venue_place=db.Column(db.String(30), nullable=False)
    venue_capacity=db.Column(db.Integer, nullable=False)
    venue_creator_id=db.Column(db.Integer, nullable=False)
    venue_image=db.Column(db.String(50), nullable=False)

class Ratings(db.Model):
    __tablename__="ratings"
    rating_id=db.Column(db.Integer, nullable=False, primary_key=True)
    ratings=db.Column(db.Integer, nullable=False)
    ruser_id=db.Column(db.Integer, nullable=False)
    rshow_id=db.Column(db.Integer, nullable=False)
    rvenue_id=db.Column(db.Integer, nullable=False)


#initialising database
db.init_app(app)
app.app_context().push()


#creating database if not already exists
if os.path.exists("/booktheshow.sqlite3")==False:
    db.create_all()



def validate_username(a):
    if len(a)<4 or len(a)>20:
        return "length_error"
    if not a.isalnum():
        return "not_alphanumeric"
    return a
    
def validate_password(pwd):
    if len(pwd)<8 or len(pwd)>20:
        return "pwd_length"
    return pwd

def validate_email(mail):
    pattern = r'^[a-zA-Z0-9.]+@[a-zA-Z0-9]+\.[a-z]{2,}$'
    if re.match(pattern, mail):
        return True
    return False


def validate_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        if date_obj.date() <= datetime.now().date():
            raise ValueError('Date should be greater than today.')
    except ValueError:
        return False
    return True


#-------------------------------------------HOMEPAGE-----------------------------------------
@app.route('/', methods=["GET", "POST"])
def homepage():
    if request.method=="GET":
        return render_template("homepage.html")
    if request.method=="POST":
        login_type = request.form.get("login_type")
        if login_type=="admin":
            return redirect("/admin_login")
        if login_type=="user":
            return redirect("/user_login")



#--------------------------------------------ADMIN LOGIN------------------------------------
@app.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    if request.method=="GET":
        return render_template("ad_login.html")
    if request.method=="POST":
        usrname=request.form["ad_username"]
        passwrd=request.form["passwrd"]
        if validate_username(usrname)!=usrname:
            flash("Username length should be between 4 and 20 alphanumeric characters", "uname_error")
            return render_template("ad_login.html", usrname=usrname)
        adusrname=Admin.query.filter_by(ad_username=usrname).all()
        if len(adusrname)==0:
            flash("No Admin Exists with this Username! Enter correct credentials or Register as New Admin", "no_user")
            return redirect("/admin_login")
        if len(adusrname)>0:
            ad_uname=Admin.query.filter_by(ad_username=usrname).first()
            pwd=ad_uname.ad_pwd
            session["usr"]=usrname
            session["logged_in"]=True
            if pwd==passwrd:
                flash("Logged in successfully! Welcome to your dashboard", "success")
                return redirect("/admin")
            if validate_password(passwrd)!=passwrd:
                flash("Length of password should be at least 8 and at max 20 characters", "pwd_error")
                return render_template("ad_login.html", usrname=usrname)
            flash("Wrong password!", "error")
            return render_template("ad_login.html", usrname=usrname)
                




#------------------------ADMIN REGISTER----------------------------------------------------
@app.route("/admin_register", methods=["GET", "POST"])
def admin_register():
    if request.method=="GET":
        return render_template("admin_register.html")
    if request.method=="POST":
        ad_fname=request.form["ad_fname"]
        ad_lname=request.form["ad_lname"]
        ad_loc=request.form["loc"]
        ad_email=request.form["email"]
        if not validate_email(ad_email):
            flash("Enter a valid email.","email_error")
            return render_template("admin_register.html", fname=ad_fname, lname=ad_lname, loc=ad_loc)
        ad_uname=request.form["ad_username"]
        if validate_username(ad_uname)!=ad_uname:
            flash("Length of username should be between 4 and 20 alphanumeric characters", "uname_error")
            return render_template("admin_register.html", fname=ad_fname, lname=ad_lname, loc=ad_loc, email=ad_email )
        ad_passwrd=request.form["ad_pwd"]
        if validate_password(ad_passwrd)!=ad_passwrd:
            flash("Length of password should be at least 8 and at max 20 characters", "pwd_error")
            return render_template("admin_register.html", fname=ad_fname, lname=ad_lname, uname=ad_uname, loc=ad_loc, email=ad_email )      
        ad_img=request.files["admin_img"]
        file_name=secure_filename(ad_img.filename)
        if file_name!="":
            file_ext=os.path.splitext(file_name)[1]
            renamed_file_name=ad_uname+file_ext
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            ad_img.save(os.path.join(app.config['UPLOAD_PATH'], renamed_file_name))
        adusrname=Admin.query.filter_by(ad_username=ad_uname).all()
        if len(adusrname)!=0:
            flash("Username already exists! Try some other username.","usrname_exist")
            return render_template("admin_register.html", fname=ad_fname, lname=ad_lname, uname=ad_uname, loc=ad_loc, email=ad_email )
        ad_data=Admin(ad_username=ad_uname, ad_fname=ad_fname,ad_lname=ad_lname,ad_loc=ad_loc,ad_email=ad_email,ad_pwd=ad_passwrd, ad_img=renamed_file_name)
        db.session.add(ad_data)
        db.session.commit()
        flash("Registered as admin successfully", "success")
        return redirect("/admin_login")



#---------------------ADMIN LOGOUT---------------------------------------------------------
@app.route("/admin_logout", methods=["GET", "POST"])
def ad_logout():
    session.pop("usr", None)
    session["logged_in"]=False
    flash("Logged out successfully!", "success")
    return redirect("/")



#----------------USER LOGIN-----------------------------------------------------
@app.route('/user_login', methods=["GET", "POST"])
def user_login():
    if request.method=="GET":
        return render_template("user_login.html")
    if request.method=="POST":
        usrname=request.form["username"]
        passwrd=request.form["passwrd"]
        if validate_username(usrname)!=usrname:
            flash("Length of username should be between 4 and 20 alphanumeric characters", "uname_error")
            return render_template("user_login.html", usrname=usrname)
        usr=Users.query.filter_by(user_username=usrname).all()
        if len(usr)==0:
            flash("No User Exists with this Username! Enter correct credentials or Register as New User", "no_user")
            return redirect("/user_login")
        if len(usr)>0:
            user_uname=Users.query.filter_by(user_username=usrname).first()
            session["user"]=usrname
            session["user_logged_in"]=True
            pwd=user_uname.user_pwd
            if pwd==passwrd:
                flash("Logged in successfully! Welcome to your dashboard", "success")
                return redirect("/dashboard")
            if validate_password(passwrd)!=passwrd:
                flash("Length of password should be at least 8 and at max 20 characters", "pwd_error")
                return render_template("user_login.html", usrname=usrname)
            flash("Wrong password!", "error")
            return render_template("user_login.html", usrname=usrname)



#------------------------------------------------USER REGISTER----------------------------------------------------
@app.route("/user_register", methods=["GET", "POST"])
def user_register():
    if request.method=="GET":
        return render_template("user_register.html")
    if request.method=="POST":
        u_fname=request.form["u_fname"]
        u_lname=request.form["u_lname"]
        u_loc=request.form["u_location"]
        u_email=request.form["u_email"]
        if not validate_email(u_email):
            flash("Enter a valid email.","email_error")
            return redirect("/user_register")
        u_uname=request.form["u_username"]
        if validate_username(u_uname)!=u_uname:
            flash("Length of username should be between 4 and 20 alphanumeric characters", "uname_error")
            return redirect("/user_register")
        u_passwrd=request.form["u_pwd"]
        if validate_password(u_passwrd)!=u_passwrd:
            flash("Length of password should be at least 8 and at max 20 characters", "pwd_error")
            return redirect("/user_register")
        u_img=request.files["u_img"]
        uusrname=Users.query.filter_by(user_username=u_uname).all()
        if len(uusrname)!=0:
            flash("Username already exists! Try some other username.","usrname_exist")
            return redirect("/user_register")
        file_name=secure_filename(u_img.filename)
        if file_name!="":
            file_ext=os.path.splitext(file_name)[1]
            renamed_file_name=u_uname+file_ext
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            u_img.save(os.path.join(app.config['UPLOAD_PATH'], renamed_file_name))
        u_data=Users(user_username=u_uname, user_fname=u_fname,user_lname=u_lname,user_email=u_email ,user_pwd=u_passwrd,user_loc=u_loc, user_img=renamed_file_name)
        db.session.add(u_data)
        db.session.commit()
        flash("Registered as user successfully", "success")
        return redirect("/user_login")

#---------------------------USER LOGOUT-----------------------------------------------------
@app.route("/user_logout", methods=["GET", "POST"])
def user_logout():
    session.pop("user", None)
    session["user_logged_in"]=False
    flash("Logged out successfully!", "success")
    return redirect("/user_login")







#------------------------------------------ADMIN DASHBOARD---------------------------------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method=="GET":
        if 'logged_in' in session.keys():
            usrname=session["usr"]
            adusr=Admin.query.filter_by(ad_username=usrname).first()
            ad_id=adusr.admin_id
            venue_details=Venue.query.filter_by(venue_creator_id=ad_id).all()
            return render_template("ad_dashboard.html", admin_username=usrname, ven_det=venue_details)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")
    



#----------------------------------------------CREATE VENUE-----------------------------------------------------
@app.route("/admin/create_venue", methods=["GET", "POST"])
def create_venue():
    if request.method=="GET":
        if 'logged_in' in session.keys():
            usrname=session["usr"]
            return render_template("add_venue.html", admin_username=usrname)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")
    if request.method=="POST":
        ven_name=request.form["ven_name"]
        ven_loc=request.form["ven_loc"]
        ven_plac=request.form["ven_place"]
        ven_cap=request.form["ven_cap"]
        usrname=session["usr"]
        ven_image=request.files["ven_img"]
        ven_creator=Admin.query.filter_by(ad_username=usrname).first()
        ven_creator_id=ven_creator.admin_id
        file_name=secure_filename(ven_image.filename)
        if file_name!="":
            file_ext=os.path.splitext(file_name)[1]
            renamed_file_name=ven_loc+"_"+ven_plac+file_ext
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            ven_image.save(os.path.join(app.config['UPLOAD_PATH'], renamed_file_name))
        venue_data=Venue(venue_name=ven_name, venue_place=ven_plac, venue_location=ven_loc, 
                         venue_capacity=ven_cap, venue_creator_id=ven_creator_id, 
                         venue_image=renamed_file_name)
        db.session.add(venue_data)
        db.session.commit()
        flash("Venue created successfully!","success")
        return redirect("/admin")



#------------------------------------------------CREATE SHOW INSIDE VENUE------------------------------------------
@app.route("/admin/<ven_id>/create_show", methods=["GET", "POST"])
def create_show(ven_id):
    if request.method=="GET":
        if 'logged_in' in session.keys():
            usrname=session["usr"]
            return render_template('add_show.html', admin_username=usrname, ven_id=ven_id )
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")
    if request.method=="POST":
        show_cap=Venue.query.filter_by(venue_id=ven_id).first().venue_capacity
        show_admin_id=Venue.query.filter_by(venue_id=ven_id).first().venue_creator_id
        s_name=request.form["s_name"]
        rating=request.form["rating"]
        time=request.form["time"]
        date=request.form["date"]
        if not validate_date(date):
            flash("Date must be after today","date_error")
            return redirect("/admin/"+ven_id+"/create_show")
        tag=request.form["tag"]
        price=request.form["price"]
        show_image=request.files["show_img"]
        file_name=secure_filename(show_image.filename)
        if file_name!="":
            file_ext=os.path.splitext(file_name)[1]
            renamed_file_name=ven_id+"_"+s_name+file_ext
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            show_image.save(os.path.join(app.config['UPLOAD_PATH'], renamed_file_name))
        show_data=Shows(show_name=s_name, show_rating=rating, show_time=time, 
                        show_capacity=show_cap, show_date=date, show_tag=tag, 
                        show_price=price, show_venue_id=ven_id,show_admin_id=show_admin_id,
                        show_revenue=0, show_image=renamed_file_name)
        db.session.add(show_data)
        db.session.commit()
        flash("Show created successfully!","success")
        return redirect("/admin/"+ven_id+"/shows")



#------------------------------------------LISTING AVAILABLE SHOWS-------------------------------------------------
@app.route("/admin/<ven_id>/shows", methods=["GET", "POST"])
def shows(ven_id):
    if request.method=="GET":
        if 'logged_in' in session.keys():
            usrname=session["usr"]
            shows=Shows.query.filter_by(show_venue_id=ven_id).all()
            return render_template("shows.html", admin_username=usrname, ven_id=ven_id, show_det=shows)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")
    


#-------------------------------------------UPDATING VENUE---------------------------------------------------------
@app.route("/admin/<ven_id>/update", methods=["GET", "POST"])
def update_venue(ven_id):
    if request.method=="GET":
        if 'logged_in' in session.keys():
            usrname=session["usr"]
            venue_details=Venue.query.filter_by(venue_id=ven_id).first()
            return render_template("update_venue.html", ven_det=venue_details, admin_username=usrname)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")
    if request.method=="POST":
        venue_details=Venue.query.filter_by(venue_id=ven_id).first()
        ven_loc=venue_details.venue_location
        ven_plac=venue_details.venue_place
        ven_name=request.form["ven_name"]
        ven_image=request.files["ven_img"]
        venue_details.venue_name=ven_name
        file_name=secure_filename(ven_image.filename)
        if ven_image:
            if file_name!="":
                file_ext=os.path.splitext(file_name)[1]
                renamed_file_name=ven_loc+"_"+ven_plac+file_ext
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                ven_image.save(os.path.join(app.config['UPLOAD_PATH'], renamed_file_name))
            venue_details.venue_image=renamed_file_name 
        db.session.commit()
        flash("Venue details updated successfully!", "success")
        return redirect("/admin")



#--------------------------------------DELETING VENUE----------------------------------------------------------
@app.route("/admin/<ven_id>/delete", methods=["GET", "POST"])
def delete_ven(ven_id):
    if request.method=="GET":
        if session["logged_in"]:
            usrname=session["usr"]
            return render_template("delete_venue.html", admin_username=usrname, ven_id=ven_id)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")



#------------------------------------COMFIRMED DELETING VENUE-------------------------------------------------
@app.route("/admin/<ven_id>/delete_venue", methods=["GET", "POST"])
def delete_venue(ven_id):
    venue = Venue.query.filter_by(venue_id=ven_id).first()
    shows=Shows.query.filter_by(show_venue_id=venue.venue_id).all()
    bookings=Bookings.query.filter_by(bvenue_id=venue.venue_id).all()
    ratings=Ratings.query.filter_by(rvenue_id=venue.venue_id).all()
    if request.method=="GET":
        if 'logged_in' in session.keys():
            file_path = os.path.join(app.config['UPLOAD_PATH'], venue.venue_image)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(venue)
            for show in shows:
                file_path = os.path.join(app.config['UPLOAD_PATH'], show.show_image)
                if os.path.exists(file_path):
                    os.remove(file_path)                
                db.session.delete(show)
            if len(bookings)>0:
                for booking in bookings:
                    db.session.delete(booking)
            if len(ratings)>0:
                for rating in ratings:
                    db.session.delete(rating)
            db.session.commit()
            flash("Venue deleted successfully!","success")
            return redirect("/admin")
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")




#----------------------------------------------UPDATING SHOWS--------------------------------------------
@app.route("/admin/<ven_id>/<show_id>/update", methods=["GET", "POST"])
def update_show(ven_id, show_id):
    if request.method=="GET":
        if 'logged_in' in session.keys():
            usrname=session["usr"]
            show_detail=Shows.query.filter_by(show_id=show_id).first()
            return render_template("update_show.html", show_detail=show_detail, admin_username=usrname, ven_id=ven_id)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")
    if request.method=="POST":
        show_details=Shows.query.filter_by(show_id=show_id).first()
        s_name=show_details.show_name
        show_rating=request.form["rating"]
        show_time=request.form["time"]
        show_pric=request.form["price"]
        date=request.form["date"]
        usrname=session["usr"]
        if not validate_date(date):
            flash("Date must be after today","date_error")
            return render_template("update_show.html", show_detail=show_details, admin_username=usrname, ven_id=ven_id)
        show_details.show_rating=show_rating
        show_details.show_time=show_time
        show_details.show_price=show_pric
        show_details.show_date=date    ####
        show_image=request.files["show_img"]
        file_name=secure_filename(show_image.filename)
        if show_image:
            if file_name!="":
                file_ext=os.path.splitext(file_name)[1]
                renamed_file_name=ven_id+"_"+s_name+file_ext
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                show_image.save(os.path.join(app.config['UPLOAD_PATH'], renamed_file_name))
            show_details.show_image=renamed_file_name
        db.session.commit()
        flash("Show details updated successfully!","success")
        return redirect("/admin/"+ven_id+"/"+"shows")
    

#------------------------------------------------DELETING SHOW-------------------------------------------------
@app.route("/admin/<ven_id>/<show_id>/delete", methods=["GET", "POST"])
def delete_sho(ven_id, show_id):
    if request.method=="GET":
        if session["logged_in"]:
            usrname=session["usr"]
            return render_template("delete_show.html", admin_username=usrname, ven_id=ven_id, show_id=show_id)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")



#-----------------------------------------------CONFIRM DELETING SHOW---------------------------------------------
@app.route("/admin/<ven_id>/<show_id>/delete_show", methods=["GET", "POST"])
def delete_show(ven_id, show_id):
    show = Shows.query.filter_by(show_id=show_id).first()
    bookings=Bookings.query.filter_by(bshow_id=show_id).all()
    ratings=Ratings.query.filter_by(rshow_id=show_id).all()
    if request.method=="GET":
        if 'logged_in' in session.keys():
            file_path = os.path.join(app.config['UPLOAD_PATH'], show.show_image)
            if os.path.exists(file_path):
                os.remove(file_path)            
            db.session.delete(show)
            if len(bookings)>0:
                for booking in bookings:
                    db.session.delete(booking)
            if len(ratings)>0:
                for rating in ratings:
                    db.session.delete(rating)
            db.session.commit()
            flash("Show deleted successfully!","success")
            return redirect("/admin/"+ven_id+"/"+"shows")
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")



#---------------------------------------------ADMIN PROFILE-----------------------------------------------------
@app.route("/a_profile", methods=["GET", "POST"])
def a_profile():
    if request.method=="GET":
        if 'logged_in' in session.keys():
            usrname=session["usr"]
            admin_prof=Admin.query.filter_by(ad_username=usrname).first()
            return render_template("a_profile.html", admin_det=admin_prof)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/admin_login")




#---------------------------------------------USER DASHBOARD---------------------------------------------------
@app.route("/dashboard", methods=["GET", "POST"])
def user_dashboard():
    if request.method=="GET":
        if 'user_logged_in' in session.keys():
            usrname=session["user"]
            user=Users.query.filter_by(user_username=usrname).first()
            venues=Venue.query.filter(Venue.venue_place.ilike(user.user_loc)).all()
            shows=Shows.query.all()
            return render_template("user_dashboard.html", usr_usrname=usrname, venues=venues, shows=shows)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/user_login")



#-----------------------------------------BOOKING SHOW-------------------------------------------------
@app.route("/dashboard/book/<show_id>", methods=["GET", "POST"])
def booking(show_id):
    if request.method=="GET":
        if 'user_logged_in' in session.keys():
            usr_usrname=session["user"]
            show_det=Shows.query.filter_by(show_id=show_id).first()
            venue_det=Venue.query.filter_by(venue_id=show_det.show_venue_id).first()
            if int(show_det.show_capacity)==0:
                flash("The show is Housefull. Please try in some other venue.", "housefull")
                return redirect("/dashboard")
            return render_template("booking.html", show_details=show_det, venue_details=venue_det, usr_usrname=usr_usrname)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/user_login")
    if request.method=="POST":
        no_of_seats=request.form["no_of_seats"]
        if type(no_of_seats)==str or type(no_of_seats)==int:
            try:
                session["seats"]=int(no_of_seats)
            except ValueError:
                flash("Enter a positive integer", "int_error")
                return redirect("/dashboard/book/"+show_id)
        show_det=Shows.query.filter_by(show_id=show_id).first()
        if int(no_of_seats)>int(show_det.show_capacity):
            flash("Housefull ! Please enter less seats than available.","low_seat_count")
            return redirect("/dashboard/book/"+show_id)
        return redirect("/dashboard/booking/"+show_id)





#------------------------------------------CONFIRM BOOKING SHOW-------------------------------------------------
@app.route("/dashboard/booking/<show_id>", methods=["GET", "POST"])
def booking_total(show_id):
    if request.method=="GET":
        if 'user_logged_in' in session.keys():
            usr_usrname=session["user"]
            show_det=Shows.query.filter_by(show_id=show_id).first()
            no_of_seats=session["seats"]
            total_price=no_of_seats*int(show_det.show_price)
            show_det.show_revenue+=total_price
            db.session.commit()
            return render_template("booking_total.html", usr_usrname=usr_usrname,show_det=show_det, no_of_seats=no_of_seats, total_price=total_price)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/user_login")
    if request.method=="POST":
        if request.form["whether_confirm_or_not"]=="no":
            flash("Booking Cancelled", "error")
            return redirect("/dashboard")
        if request.form["whether_confirm_or_not"]=="confirm":
            now=datetime.now()
            usr_usrname=session["user"]
            buser_id=Users.query.filter_by(user_username=usr_usrname).first().user_id
            bshow_id=show_id
            show_det=Shows.query.filter_by(show_id=show_id).first()
            bvenue_id=show_det.show_venue_id
            booked=Bookings(booking_date_time=now, buser_id=buser_id, bshow_id=bshow_id, bvenue_id=bvenue_id)
            db.session.add(booked)
            show_det.show_capacity=int(show_det.show_capacity)-int(session["seats"])
            db.session.commit()
            flash("Booked successfully", "success")
            return redirect("/dashboard")



#--------------------------------------------------USER PROFILE--------------------------------------------------
@app.route("/user_profile", methods=["GET", "POST"])
def user_profile():
    if request.method=="GET":
        if 'user_logged_in' in session.keys():
            usrname=session["user"]
            user_prof=Users.query.filter_by(user_username=usrname).first()
            return render_template("u_profile.html", user_det=user_prof)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/user_login")



#----------------------------------------------USER BOOKINGS--------------------------------------------------------
@app.route("/my_bookings",methods=["GET"])
def my_bookings():
    if request.method=="GET":
        if 'user_logged_in' in session.keys():
            usrname=session["user"]
            user_id=Users.query.filter_by(user_username=usrname).first().user_id
            booking_det=Bookings.query.filter_by(buser_id=user_id).order_by(Bookings.booking_date_time.desc()).all()
            return render_template("bookings_show.html", bookings=booking_det, Venues=Venue, Shows=Shows)
        flash("You are not logged in! Please login first.", "unauthorised")
        return redirect("/user_login") 


#------------------------SEARCHING VENUES USING NAMES, SHOWS USING NAMES, TAGS/GENRE------------
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method=="GET":
        if 'user_logged_in' in session.keys():
            myquery=request.args.get("my_query")
            my_query="%{}%".format(myquery)
            searched_venues=Venue.query.filter(or_(Venue.venue_name.ilike(my_query), Venue.venue_place.ilike(my_query))).all()
            searched_shows=Shows.query.filter(or_(Shows.show_name.ilike(my_query), Shows.show_tag.ilike(my_query), Shows.show_rating.ilike(my_query))).all()
            return render_template("searched_results.html", venues=searched_venues, shows=searched_shows)




#-------------------------------------RATING SHOW AS PER VENUE--------------------------------------------------------
@app.route("/rate/<show_id>", methods=["GET", "POST"])
def rateshow(show_id):
    if request.method=="GET":
        if 'user_logged_in' in session.keys():
            usrname=session["user"]
            user_id=Users.query.filter_by(user_username=usrname).first().user_id
            show=Shows.query.filter_by(show_id=show_id).first()
            return render_template("ratings.html", show_det=show)
        return redirect("/user_login")
    if request.method=="POST":
        show=Shows.query.filter_by(show_id=show_id).first()
        usrname=session["user"]
        user_id=Users.query.filter_by(user_username=usrname).first().user_id
        rated_user_id_per_show=Ratings.query.filter_by(rshow_id=show_id)
        ruser_id_list_per_show=[rating.ruser_id for rating in rated_user_id_per_show]
        if user_id in ruser_id_list_per_show:
            flash("You have already rated", category="error")
            return redirect("/my_bookings")
        rating_value=request.form.get("rating")
        rating=Ratings(ratings=rating_value, ruser_id=user_id, rshow_id=show.show_id, rvenue_id=show.show_venue_id)
        db.session.add(rating)
        db.session.commit()
        ratings_per_show=Ratings.query.filter_by(rshow_id=show_id).all()
        rating_list=[int(rating.ratings) for rating in ratings_per_show]
        avg_rating=sum(rating_list)/len(rating_list)
        show_det=Shows.query.filter_by(show_id=show_id).first()
        show_det.show_rating=avg_rating
        db.session.commit()
        flash("Successfully Rated the Show!", "success")
        return redirect("/my_bookings")



#----------------------------VENUE DETAILS-------------------------------------------------
@app.route("/venue_details/<ven_id>", methods=["GET"])
def show_venue(ven_id):
    if request.method=="GET":
        if 'user_logged_in' in session.keys():
            venue_det=Venue.query.filter_by(venue_id=ven_id).first()
            show_det=Shows.query.filter_by(show_venue_id=venue_det.venue_id).all()
            return render_template("venue_details.html", venue=venue_det, shows=show_det)
        return redirect("/")





#-----------------------SHOW DETAILS---------------------------------
@app.route("/show/<show_id>", methods=["GET"])
def show_details(show_id):
    if request.method=="GET":
        if 'user_logged_in' in session.keys():
            show_det=Shows.query.filter_by(show_id=show_id).first()
            return render_template("show_details.html", show=show_det)
        return redirect("/")



#---------------------------------------SUMMARY FOR ADMIN-------------------------------------------------
@app.route("/summary", methods=["GET"])
def summary():
    if request.method=="GET":
        if 'logged_in' in session.keys():
            usrname=session["usr"]
            aduser_id=Admin.query.filter_by(ad_username=usrname).first().admin_id
            booking_det=Bookings.query.all()
            show_det=Shows.query.filter_by(show_admin_id=aduser_id).all()
            sid_list=[s.show_id for s in show_det]
            bsid_list=[bs.bshow_id for bs in booking_det]
            b_sid_aid=[]
            for sid in sid_list:
                if sid in bsid_list:
                    b_sid_aid.append(sid)
            genre_revenue={}
            for sid in b_sid_aid:
                show_d=Shows.query.filter_by(show_id=sid).first()
                if show_d.show_tag not in genre_revenue:
                    genre_revenue[show_d.show_tag]=show_d.show_revenue
                else:
                    genre_revenue[show_d.show_tag]+=show_d.show_revenue
            if len(b_sid_aid)!=0:
                with app.app_context():
                    sns.barplot(x=list(genre_revenue.keys()), y=list(genre_revenue.values()))
                    plt.xlabel("Genre")
                    plt.ylabel("Revenue")
                    plt.title("Revenue by Genre")
                    plt.savefig(os.path.join(app.config['UPLOAD_PATH'], "revenue.jpg"))
            return render_template("summary.html", b_sid_aid=b_sid_aid)
        return redirect("/")
    

#Running the app
if __name__=="__main__":
    app.debug=True
    app.run()