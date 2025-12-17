from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('patients.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Вхід виконано успішно!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('patients.index'))
        else:
            flash('Невірне ім\'я користувача або пароль.', 'danger')
    
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('auth.login'))