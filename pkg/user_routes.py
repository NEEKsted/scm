import os,random
from functools import wraps
from flask import render_template,flash,url_for,redirect,flash,url_for,make_response,request,session,jsonify
from sqlalchemy import or_
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,csrf
from pkg.scmmodels import db,User,Country,Audio#,State
from pkg.forms import LoginForm,search #RegisterForm,

from functools import wraps
from flask import session, flash, redirect, url_for

def login_required(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if session.get('useronline'):  # This checks if 'useronline' exists and is truthy
            return f(*args, **kwargs)
        else:
            flash('You must be logged in to access this page', category='error')
            return redirect(url_for('login_page'))  # Assuming your login route is called 'login'
    return check_login
    
@app.route("/scm/user-home/")
def login_home_page():
    id = session.get('useronline')
    deet = User.query.get(id)
    deets = session.get(id)
    audio = db.session.query(Audio).all()
    form = search()
    return render_template("user/home.html",id=id,deet=deet,deets=deets,audio=audio,form=form)

@app.route("/")
@app.route("/scm/home/")
def home_page():
    id = session.get('useronline')
    deet = User.query.get(id)
    deets = session.get(id)
    audio = db.session.query(Audio).all()
    form = search()
    return render_template("user/home_layout.html",id=id,deet=deet,deets=deets,audio=audio,form=form)

@app.route("/scm/search/")
def search_audio():
    form = search()
    results = Audio.query.filter(
        or_(
            Audio.audio.ilike(f"%{form}%"),  # Search for the term in the 'audio' column
            Audio.lyricist.ilike(f"%{form}%")  # Search for the term in the 'lyricist' column
        )
    ).all()
    
    return redirect("user/home_layout.html",results=results,form=form)

@app.route("/scm/register/", methods=['POST', 'GET'])
def user_register():
    id = session.get('useronline')
    deets = User.query.get(id)
    country_list = db.session.query(Country).all()  # Get all countries from the database
    # state_list = State.query.filter_by(country_id=id).all()
    audio_list = db.session.query(Audio).all()

    if request.method == "GET":
        return render_template(
            'user/registeration.html',  # This is the template you are rendering
            id=id,
            deets=deets,
            country=country_list,  # Pass the list of countries to the template
            audio=audio_list,
            # state=state_list
        )
    
    if request.method == "POST":
        
        
        # Handle form submission
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        country = request.form.get('country')  # Get the selected country ID from the form
        # state = request.form.get('state')
        address = request.form.get('address')
        password = request.form.get('password')
        
        # Hash the password before storing
        hashed_password = generate_password_hash(password)
        
        # Create new user
        new_user = User(
            user_fname=fname,
            user_lname=lname,
            user_email=email,
            user_country=country,  # Store the selected country
            # user_state=state,
            user_address=address,
            user_password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account Created!", category='success')
        return redirect('/scm/login/')

@app.route("/scm/login/",methods=['GET','POST'])
def login_page():
    id = session.get('useronline')
    deet = db.session.query(User).filter(User.user_name=='',User.user_gen=='').first()
    audio = db.session.query(Audio).filter(Audio.lyricist).count()
    
    form = LoginForm()
    if form.validate_on_submit:
        email = form.email.data
        pwd = form.password.data
        row_record = db.session.query(User).filter(User.user_email == email).first()
        if row_record:
            hashed_pwd = row_record.user_password
            valid = check_password_hash(hashed_pwd,pwd)
            if valid:
                id = row_record.user_id
                session['useronline'] = id
                if deet:
                    flash('Access GRANTED!, welcome to your SPACE.',category='success')
                    return redirect('/scm/library/')
                else:
                    flash("Please Update your account username and genre if not up to date, to ease accessibilty")
                    return redirect('/scm/profile_picture/')
            else:
                flash('Access DENIED! Incorrect Details Supplied',category='error')
                return render_template('user/login.html',form=form)
        else:
            flash('Access NOT GRANT! Account Match not found',category='Invalid')
            return render_template('user/login.html',form=form)
    else:
        flash("welcome please fill all fields to Login")
        return redirect('/scm/login/',deet=deet,audio=audio)
    
@app.route("/scm/profile_picture/", methods=['GET', 'POST'])
def change_profilepicture():
    id = session.get('useronline')
    
    if not id:
        flash("You need to be logged in to update your profile picture", category='error')
        return redirect(url_for('login'))  # Redirect to login if no user is found
    
    deets = User.query.get(id)
    oldpix = deets.user_pix

    if request.method == "GET":
        # Pass the current profile picture to the template if it's available
        return render_template("user/update.html", profilepix=oldpix,deets=deets)

    else:  # POST request
        profilepix = request.files.get('profilepix')

        if not profilepix:
            flash('Please select an image file (jpg, png, jpeg)', category='error')
            return render_template("user/update.html", profilepix=oldpix,deets=deets)
        
        filename = profilepix.filename
        
        if filename == '':
            flash('Please select an image file (jpg, png, jpeg)', category='error')
            return render_template("user/update.html", profilepix=oldpix)

        # Extract file extension and check if it's allowed
        name, ext = os.path.splitext(filename)
        allowed = ['.jpg', '.png', '.jpeg']
        
        if ext.lower() in allowed:
            # Generate a unique filename using UUID to avoid collisions
            final_name = f"{random.randint(100000, 999999)}{ext}"
            file_path = os.path.join('pkg', 'static', 'user_pix', final_name)

            # Save the uploaded file
            profilepix.save(file_path)

            # Update the user's profile picture path in the database
            deets.user_pix = final_name
            db.session.commit()

            # If there's an old picture, delete it (if it exists)
            if oldpix:
                oldpix_path = os.path.join('pkg', 'static', 'user_pix', oldpix)
                if os.path.exists(oldpix_path):
                    try:
                        os.remove(oldpix_path)
                    except Exception as e:
                        flash(f"Could not delete old image: {str(e)}", category='error')

            flash("Profile picture updated successfully!", category='success')
            return redirect(url_for('change_profilepicture', profilepix=final_name))  # Assuming user_profile handles the profile picture display
        else:
            flash('Extension not allowed (jpg, png, jpeg)', category='error')
            return redirect(url_for('change_profilepicture'))  # Redirect back to profile picture page

@app.route('/scm/genre-username-update/', methods=["POST", "GET"]) 
@login_required
def usergen_username_update():
    id = session.get('useronline')  # Get the logged-in user's ID
    deets = User.query.get(id)  # Fetch user details from the database
    country = db.session.query(Country).all()  # Fetch all countries
    form = search()  # Assuming you have a form object for additional functionality

    if request.method == 'GET':
        # Render the form with user details
        return render_template('user/update.html', deets=deets, country=country, form=form)

    else:  # POST request
        # Get the form data using request.form.get() or request.form['field_name']
        username = request.form.get('username')        
        genre = request.form.get('genre')

        if username != '' or username == deets.user_name or username not in deets.user_name and genre != '' or genre == deets.user_gen:
            row_record = db.session.query(User).filter(User.user_name == username).first()
            if row_record:
                flash(f'User with username {username} exists')
                return redirect(url_for('user_contact_info_update'))

            # You can update the user details and commit to the database
            deets.user_name = username        
            deets.user_gen = genre

            # Commit the changes to the database
            try:
                db.session.commit()
                flash('Username and Genre: Update successful', category='success')
            except Exception as e:
                db.session.rollback()  # Rollback in case of error
                flash(f'Error occurred: {str(e)}', category='error')
        else:
            flash('Username or Genre fields are empty!', category='error')
            return render_template('user/update.html', deets=deets, country=country, form=form)

        # Redirect to the user profile page
        return redirect(url_for('usergen_username_update'))

@app.route('/scm/contact-info-update/', methods=["POST", "GET"]) 
@login_required
def user_contact_info_update():
    id = session.get('useronline')  # Get the logged-in user's ID
    deets = User.query.get(id)  # Fetch user details from the database
    country = db.session.query(Country).all()  # Fetch all countries
    form = search()  # Assuming you have a form object for additional functionality

    if request.method == 'GET':
        # Render the form with user details
        return render_template('user/update.html', deets=deets, country=country, form=form)

    else:  # POST request
        # Get the form data using request.form.get() or request.form['field_name']       
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        if email != '' or email == deets.user_email or email not in deets.user_email and phone != '' or phone == deets.user_phone:
            row_record = db.session.query(User).filter(User.user_email == email).first()
            if row_record:
                flash(f'User with email {email} exists')
                return redirect(url_for('user_contact_info_update'))
        
            # You can update the user details and commit to the database
            deets.user_email = email
            deets.user_phone = phone

            # Commit the changes to the database
            try:
                db.session.commit()
                flash('Contact Information Update successful', category='success')
            except Exception as e:
                db.session.rollback()  # Rollback in case of error
                flash(f'Error occurred: {str(e)}', category='error')
        else:
            flash('Contact Information fields are empty!', category='error')
            return render_template('user/update.html', deets=deets, country=country, form=form)

        # Redirect to the user profile page
        return redirect(url_for('user_contact_info_update'))

@app.route('/scm/password-update/', methods=["POST", "GET"]) 
@login_required
def user_password_update():
    id = session.get('useronline')  # Get the logged-in user's ID
    deets = User.query.get(id)  # Fetch user details from the database
    country = db.session.query(Country).all()  # Fetch all countries
    form = search()  # Assuming you have a form object for additional functionality

    if request.method == 'GET':
        # Render the form with user details
        return render_template('user/update.html', deets=deets, country=country, form=form)

    else:  # POST request
        # Get the form data using request.form.get() or request.form['field_name']
        passcode = request.form.get('passcode')  # New password
        cnfpasscode = request.form.get('cnfnewpasscode')  # Confirm new password
        
        if passcode != '' or passcode == deets.user_password or passcode not in deets.user_password:
            # Check if password and confirm password match
            if passcode != cnfpasscode:
                flash("Passwords do not match", category='error')
                return redirect(url_for('user_profile'))

            # If the password is provided, hash and update it
            if passcode:
                hashed_pwd = generate_password_hash(passcode)
                deets.user_password = hashed_pwd

            # Commit the changes to the database
            try:
                db.session.commit()
                flash('Password Update successful', category='success')
            except Exception as e:
                db.session.rollback()  # Rollback in case of error
                flash(f'Error occurred: {str(e)}', category='error')
        else:
            flash('Password fields empty', category='error')
            return render_template('user/update.html', deets=deets, country=country, form=form)

        # Redirect to the user profile page
        return redirect(url_for('user_contact_info_update'))

     
@app.route('/scm/post/',methods=["POST","GET"])
@login_required
def post():
    id = session.get('useronline')
    deets = User.query.get(id)
    audio = db.session.query(Audio).get(id)
    if request.method == 'GET':
        return render_template('user/post.html',deets=deets,audio=audio)
    else:
        postalbum = request.files.get('audioalbum')
        postaudio = request.files.get('musicfile')
        afilename = postalbum.filename
        filename = postaudio.filename
        if filename == '' or filename == '':
            flash('please select a valid file',category='error')
            return redirect('/scm/post/')
        else:
            albumname,albumext = os.path.splitext(afilename)
            albumallowed=['.jpg','.png','.jpeg']

            audioname,audioext = os.path.splitext(filename)
            audioallowed=['.mp3', '.m4a', '.wav']
            if audioext.lower() in audioallowed and albumext.lower() in albumallowed:
                album_file_name = int(random.random()*100000)
                #splitting the filename from extension
                album_file_name = str(album_file_name) + albumext
                #sending the image file into the image files path
                postalbum.save(f'pkg/static/album/{album_file_name}')
                #giving a random filename to the doc
                audio_file_name = int(random.random()*100000)
                #splitting the filename from extension
                audio_file_name = str(audio_file_name) + audioext
                #sending the audiofile into the audio files path
                postaudio.save(f'pkg/static/audio/{audio_file_name}')

                #call db table audio
                title = request.form.get('title')
                lyricist = request.form.get('lyricist')
                quote = request.form.get('quotes')
                producer = request.form.get('producer')
                user = request.form.get('user')
                if title!='' and lyricist != '' and quote != '' or producer != '':
                    audio = Audio(
                    album = album_file_name,
                    audio = audio_file_name,
                    lyric_title = title,
                    lyricist = lyricist,
                    quotes = quote,
                    producer = producer,
                    
                    )
                    db.session.add(audio)
                    db.session.commit()
                    flash('Upload posted successfully',category='success')
                    return redirect('/scm/user-home/')
                else:
                    flash("All fields are required",category='error')
                    return redirect('/scm/post/',user=user)
            else:
                message = flash("Unexpected Filetype, require file type; Album:( .jpg, .png, .jpeg ) Audio:( .mp3, .m4a), .wav )")
                return redirect('/scm/post/',user=user)

@app.route("/scm/library/")
def space():
    id = session.get('useronline')
    deets = db.session.query(User).all()
    deet = User.query.get(id)
    form = search()
    return render_template("user/library.html",deets=deets,deet=deet,form=form)

@app.route("/scm/logout/")
@login_required
def logout_page():
    # Clear the user session
    session.pop('useronline', None)  # This will remove 'useronline' from the session if it exists
    
    # Optionally, you can also clear other session data, like user info:
    # session.pop('username', None)  # if you store username in the session
    
    # Flash a message that the user has been logged out (optional)
    flash('You have been logged out', category='info')
    
    # Redirect to the homepage or login page
    return redirect(url_for('home_page'))  # Assuming 'index' is the name of your homepage route
