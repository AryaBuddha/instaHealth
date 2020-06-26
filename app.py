from flask import Flask, redirect, url_for, render_template, request, session, flash
import requests
import os
import dotenv
from dotenv import load_dotenv, find_dotenv
import pymongo
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET')

find_dotenv()
load_dotenv()

cluster = MongoClient(os.getenv('MONGO_URL'))
db = cluster['Personal']
users_collection = db['NexTech']


@app.route('/', methods = ['GET'])
def landing():
    if request.method == 'GET':
        return render_template('landing.html')


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('register.html')

    elif request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')
        confirm_password = request.form.get('PasswordConfirm')


        if str(password) == str(confirm_password):
            session['email'] = email
            email = email.lower()
            session['password'] = password
            
            try:

                account_exists = users_collection.find_one({'Email': email})
                password_exists = account_exists['Password']
            
                flash('You already have an account!')
                return render_template('register.html')
            except:

                post = {'Email': email, 'Password': password, 'Type': 'Teacher'}
                users_collection.insert_one(post)
                return redirect(url_for('profile'))

        else:
            flash('Your passwords do not match!')
            return render_template('register.html')

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
        
    elif request.method == 'POST':
        email = request.form.get('Email')
        password = request.form.get('Password')

        return 'Good job'

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    if request.method == 'GET':
        return render_template('profile.html')

    elif request.method == 'POST':
        pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 80, debug=True)
