from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.forms import UserForm
from functools import wraps

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('У вас немає доступу до цієї сторінки.', 'danger')
            return redirect(url_for('patients.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/users')
@login_required
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users_list)

@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Користувача успішно створено!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('user_form.html', form=form, title='Додати користувача')

@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(original_username=user.username)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Дані користувача оновлено!', 'success')
        return redirect(url_for('admin.users'))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.role.data = user.role
        form.password.data = ''
    
    return render_template('user_form.html', form=form, title='Редагувати користувача', edit=True)

@admin.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if id == current_user.id:
        flash('Ви не можете видалити самого себе!', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Користувача видалено!', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/users/toggle-role/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_role(id):
    if id == current_user.id:
        flash('Ви не можете змінити власну роль!', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(id)
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    flash(f'Роль користувача змінено на {user.role}!', 'success')
    return redirect(url_for('admin.users'))