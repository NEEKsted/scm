from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField,BooleanField, RadioField,PasswordField,EmailField, StringField, IntegerField, FloatField
from wtforms.validators import DataRequired,Length,Email,EqualTo,InputRequired, Regexp, NumberRange
from flask_wtf.file import FileField,FileAllowed,FileRequired

from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date


# from flask_bootstrap import Bootstrap

# from flask_wtf import FlaskForm
# # from wtforms import SubmitField, SelectField,BooleanField, RadioField,PasswordField,EmailField, HiddenField, StringField, IntegerField, FloatField
# from wtforms.validators import InputRequired, Regexp, NumberRange



class RegisterForm(FlaskForm):
    firstname = StringField('Firstname*')
    lastname = StringField('Lastname*',validators=[DataRequired()])
    email = StringField('Email*',validators=[DataRequired(),Email()])
    country = SelectField('Select a nationality*',
        choices=[ ('', ''), ('nigeria', 'Nigeria'),
        ('canada', 'Canada'),
        ('south-africa', 'South-Africa')])
    state = StringField('Add a state of origin*',validators=[DataRequired()])
    address = StringField('Residential Address (optional)')
    password = PasswordField('enter a secured passcode*',validators=[DataRequired(), EqualTo('cnfpassword'),Length(min=8)])
    cnfpassword = PasswordField('confirm secure passcode*',validators=[DataRequired(), EqualTo('password'),Length(min=8)])
    # updated - date - handled in the route function
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email*',validators=[DataRequired(),Email()])
    password = PasswordField('enter your secured passcode*',validators=[DataRequired(), EqualTo('cnfpassword'),Length(min=8)])
    cnfpassword = PasswordField('confirm secure passcode*',validators=[DataRequired(), EqualTo('password'),Length(min=8)])
    # updated - date - handled in the route function
    submit = SubmitField('Sign In')

class search(FlaskForm):
    searching = StringField('searching for something', validators={DataRequired()})