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
    if 'email' not in session:
        if request.method == 'GET':
            return render_template('register.html')

        elif request.method == 'POST':
            email = request.form.get('Email')
            password = request.form.get('Password')
            confirm_password = request.form.get('PasswordConfirm')


            if str(password) == str(confirm_password):

                try:

                    account_exists = users_collection.find_one({'Email': email})
                    password_exists = account_exists['Password']
                
                    flash('You already have an account!')
                    return render_template('register.html')
                except:

                    post = {'Email': email, 'Password': password, 'Type': 'Teacher'}
                    users_collection.insert_one(post)
                    return redirect(url_for('teacherProfile'))
                    session['email'] = email
                    email = email.lower()
                    session['password'] = password
                    

            else:
                flash('Your passwords do not match!')
                return render_template('register.html')

    else:
        return redirect(url_for('teacherProfile'))

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    if 'email' not in session:
        if request.method == 'GET':
            return render_template('signin.html')
            
        elif request.method == 'POST':
            email = request.form.get('Email')
            password = request.form.get('Password')

            try:

                account_exists = users_collection.find_one({'Email': email, 'Password': password})
                
                if account_exists['Type'] == 'Student':
                    return redirect(url_for('studentprofile')) 
                
                session['email'] = account_exists['Email']
                session['password'] = account_exists['Password']

            except:
                flash('Incorrect Username/Password!')
                return render_template('signin.html')
            
            return redirect(url_for('teacherProfile'))
    else:
        return redirect(url_for('teacherProfile'))

@app.route('/teacherprofile', methods = ['GET', 'POST'])
def teacherProfile():
    if 'email' in session:
        if request.method == 'GET':
            teacher_account = users_collection.find_one({'Email': session['email']})
            name = teacher_account['Name']
            session['name'] = name
            return render_template('teacherprofile.html', name=name)

        elif request.method == 'POST':
            pass
    else:
        return redirect(url_for('signin'))


@app.route('/studentprofile', methods = ['GET', 'POST'])
def studentProfile():
    if 'email' in session:
        if request.method == 'GET':
            student_account = users_collection.find_one({'Email': session['email']})
            teacher_name = student_account['Name']
            student_name = student_account['Teacher']
            session['name'] = name
            return render_template('teacherprofile.html', name=name)

        elif request.method == 'POST':
            pass
    else:
        return redirect(url_for('signin'))

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('email', None)
    session.pop('password', None)
    session.pop('name', None)
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 80, debug=True)
