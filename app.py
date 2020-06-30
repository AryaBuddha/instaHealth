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
            name = request.form.get('Name')


            if str(password) == str(confirm_password):

                try:

                    account_exists = users_collection.find_one({'Email': email})
                    password_exists = account_exists['Password']
                
                    flash('You already have an account!')
                    return render_template('register.html')
                except:

                    post = {'Email': email, 'Password': password, 'Type': 'Teacher', 'Name': name}
                    users_collection.insert_one(post)
                    return redirect(url_for('teacherProfile'))
                    session['email'] = email
                    email = email.lower()
                    session['password'] = password
                    

            else:
                flash('Your passwords do not match!')
                return render_template('register.html')

    else:
        if session['type'] == 'Student':
            return redirect(url_for('studentProfile'))

        else:
            return redirect(url_for('teacherProfile'))

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    if 'email' not in session:
        if request.method == 'GET':
            return render_template('signin.html')
            
        elif request.method == 'POST':
            email = request.form.get('Email').lower()
            password = request.form.get('Password')

            try:

                account_exists = users_collection.find_one({'Email': email, 'Password': password})
                session['email'] = account_exists['Email']
                session['password'] = account_exists['Password']
                session['type'] = account_exists['Type']
                if str(session['type']) == 'Student':
                    return redirect(url_for('studentProfile')) 
                


            except:
                flash('Incorrect Username/Password!')
                return render_template('signin.html')
            
            return redirect(url_for('teacherProfile'))
    else:
        if session['type'] == 'Student':
            return redirect(url_for('studentProfile'))

        else:
            return redirect(url_for('teacherProfile'))


@app.route('/teacherprofile', methods = ['GET', 'POST'])
def teacherProfile():
    if 'email' in session:
        if request.method == 'GET':
            teacher_account = users_collection.find_one({'Email': session['email']})
            name = teacher_account['Name']
            session['name'] = name
            return render_template('teacherprofile.html', name=name, type=session['type'])

        elif request.method == 'POST':
            pass
    else:
        return redirect(url_for('signin'))


@app.route('/studentprofile', methods = ['GET', 'POST'])
def studentProfile():
    if 'email' in session:
        if request.method == 'GET':
            student_account = users_collection.find_one({'Email': session['email']})
            student_name = student_account['Name']
            teacher_name = student_account['Teacher']
            session['name'] = student_name
            return render_template('studentprofile.html', name=student_name, teacher_name = teacher_name)

        elif request.method == 'POST':
            pass
    else:
        return redirect(url_for('signin'))


@app.route('/teacherprofile/userslist', methods=['GET', 'POST'])
def usersList():
    if request.method == 'GET':
        if 'email' in session and session['type'] == 'Teacher':
            student_list = users_collection.find({'Type': 'Student', 'Teacher': session['name']})
            student_names = []
            student_emails = []
            for student in student_list:
                student_names.append(student['Name'])
                student_emails.append(student['Email'])

            lencount = len(student_emails)
            count = range(0, lencount)
            print(student_emails, student_names, student_list)
            print(count) 

            return render_template('userslist.html', count = len(student_emails), emails=student_emails, names=student_names)


@app.route('/teacherprofile/userslist/<email>', methods=['GET', 'POST'])
def usersEdit(email):
    if request.method == 'GET':
        student_account = users_collection.find_one({'Email': email, 'Type': 'Student'})
        student_name = student_account['Name']

        return render_template('usersedit.html', email=email, name = student_name)
    if request.method == 'POST':
        edited_name = request.form.get('name')
        edited_email = request.form.get('email').lower()

        if len(edited_name) > 0 and len(edited_email) > 0:

            users_collection.find_one_and_update({'Email': email, 'Type': 'Student'}, {'$set' :{'Email': edited_email, 'Name': edited_name}})
            flash('User Updated!')
            return redirect(url_for('usersList'))
        else:
            flash('Please fill out both fields!')
            student_account = users_collection.find_one({'Email': email, 'Type': 'Student'})
            student_name = student_account['Name']

            return render_template('usersedit.html', email=email, name = student_name)



@app.route('/teacherprofile/userslist/newuser', methods=['GET', 'POST'])
def newUser():
    if request.method == 'GET':
        return render_template('newuser.html')

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('Password')

        if len(email) > 0 and len(name) > 0 and len(password) > 0:

            post = {'Email': email, 'Password': password, 'Type': 'Student', 'Name': name, 'Teacher': session['name']}
            users_collection.insert_one(post)

            flash('User Successfully Created!')
            return redirect(url_for('usersList'))

        else:
            flash('Please fill out all fields!')
            return render_template('newuser.html')


@app.route('/teacherprofile/userslist/deluser/<email>')
def delUser(email):
    users_collection.remove({'Email': email})
    flash('User successfully deleted!')
    return redirect(url_for('usersList'))



@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('email', None)
    session.pop('password', None)
    session.pop('name', None)
    session.pop('type', None)
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 80, debug=True)
