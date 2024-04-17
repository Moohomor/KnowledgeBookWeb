from flask import Blueprint, render_template, redirect, request
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from data.users import User
from data import db_session

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect('/')
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return render_template('login.html', message='Почта или пароль не подходят')
    login_user(user, remember=True)
    return redirect('/')


@auth.route('/signup')
def signup():
    if current_user.is_authenticated:
        return redirect('/')
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(username=username).first()
    if user:
        return render_template('signup.html', message='Уже существует учётная запись с этим email')

    user = User(email=email, username=username, password=generate_password_hash(password))
    db_sess.add(user)
    db_sess.commit()
    return redirect('/login')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
