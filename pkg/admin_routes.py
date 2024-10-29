from datetime import datetime
import os,random,string
from functools import wraps
from flask import render_template,flash,redirect,flash,url_for,make_response,request,session
# from pkg.forms import LoginForm
from sqlalchemy.sql import text

from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,csrf
from pkg.scmmodels import db,User,Scm_admin,Audio

@app.route('/scm/admin/login/', methods=['POST', 'GET'])
def admin_login():
    id = session.get('useronline')
    deets = User.query.get(id)
    if request.method == "GET":
        flash("Welcome! Please fill in all ADMIN details to log in")
        return render_template('admin/admin_login.html')
    else:
        email = request.form.get('adminemail')
        pwd = request.form.get('adminpwd')
        row_record = db.session.query(Scm_admin).filter(Scm_admin.admin_username == email).first()
        if row_record:
            hashed_pwd = row_record.admin_pwd
            valid = check_password_hash(hashed_pwd, pwd)
            if valid:
                id = row_record.admin_id
                session['useronline'] = id
                flash('Access GRANTED! Welcome to your SPACE.', category='success')
                return redirect('/scm/admin/dashboard/')
            else:
                flash('Incorrect Credentials',category='error')
                return redirect("/scm/admin/login/")
        else:
            flash('Access DENIED! Incorrect Details Supplied', category='error')
            return render_template('/scm/admin/login/')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='GET':
        return render_template('user/loginpage.html')
    else:
        email=request.form.get('email')
        pwd=request.form.get('pwd')
        record = db.session.query(User).filter(User.user_email ==email).first()
        if record:
            hashed_pwd = record.user_password
            rsp = check_password_hash(hashed_pwd,pwd)
            if rsp:
                id = record.user_id
                session['useronline']=id
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect Credentials',category='error')
                return redirect('/login')
        else:
            flash('Incorrect Invalid Credentials',category='error')
            return redirect('/login')
        
@app.route("/scm/admin/dashboard/")
def admin_dashboard():
    deets = db.session.query(User).all()
    audios = db.session.query(Audio).all()
    return render_template("admin/dashboard.html",deets=deets,audios=audios)

@app.route("/scm/admin/disable/<int:user_id>/", methods=["GET"])
def disable(user_id):
    disable= 'disable'
    deet = User.query.get(user_id)
    if deet.user_status == 'enable' or 'pending':
        deet.user_status = disable
        db.session.commit()
        flash("User disabled")
        return redirect('/scm/admin/dashboard/')
    elif deet.user_status == 'disable':
        flash("User State: Disable")
        return redirect('/scm/admin/dashboard/')
    else:
        flash('No User record found')
        return redirect('/scm/admin/dashboard/')
    
@app.route("/scm/admin/enable/<int:user_id>/", methods=["GET"])
def enable(user_id):
    enable = 'enable'
    deet = User.query.get(user_id)
    if deet.user_status == 'disable':
        deet.user_status = enable
        db.session.commit()
        flash("User disabled")
        return redirect('/scm/admin/dashboard/')
    elif deet.user_status == 'enable' or "pending":
        flash("User State: Enable")
        return redirect('/scm/admin/dashboard/')
    else:
        flash('No User record found')
        return redirect('/scm/admin/dashboard/')
    
@app.route("/scm/admin/ban/<int:audio_id>/", methods=["GET"])
def ban(audio_id):
    ban = 'bann'
    audio = Audio.query.get(audio_id)
    if audio.audio_status == 'active' or 'pending' or '':
        audio.audio_status = ban
        db.session.commit()
        flash("Audio Banned")
        return redirect('/scm/admin/dashboard/')
    elif audio.audio_status == 'bann':
        flash("Audio State: Banned")
        return redirect('/scm/admin/dashboard/')
    else:
        flash('Audio File Not Found')
        return redirect('/scm/admin/dashboard/')

@app.route("/scm/admin/unban/<int:audio_id>/", methods=["GET"])
def unban(audio_id):
    active = 'active'
    audio = Audio.query.get(audio_id)
    if audio.audio_status == 'bann' or 'pending' or '':
        audio.audio_status = active
        db.session.commit()
        flash("Audio Unbanned")
        return redirect('/scm/admin/dashboard/')
    elif audio.audio_status == 'active':
        flash("Audio State: Active")
        return redirect('/scm/admin/dashboard/')
    else:
        flash('Audio File Not Found')
        return redirect('/scm/admin/dashboard/')