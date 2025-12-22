from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Patient
from app.forms import PatientForm
from functools import wraps

patients = Blueprint('patients', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('У вас немає доступу до цієї сторінки.', 'danger')
            return redirect(url_for('patients.index'))
        return f(*args, **kwargs)
    return decorated_function

@patients.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    department = request.args.get('department', '')
    doctor = request.args.get('doctor', '')
    status = request.args.get('status', '')
    
    # Поточний місяць
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    query = Patient.query
    
    # Фільтр за поточний місяць
    query = query.filter(
        db.extract('month', Patient.admission_date) == current_month,
        db.extract('year', Patient.admission_date) == current_year
    )
    
    # Пошук
    if search:
        query = query.filter(
            db.or_(
                Patient.full_name.ilike(f'%{search}%'),
                Patient.history_number.ilike(f'%{search}%')
            )
        )
    
    # Фільтри
    if department:
        query = query.filter(Patient.department.ilike(f'%{department}%'))
    if doctor:
        query = query.filter(Patient.doctor.ilike(f'%{doctor}%'))
    if status == 'deceased':
        query = query.filter(Patient.is_deceased == True)
    elif status == 'alive':
        query = query.filter(Patient.is_deceased == False)
    
    # Сортування за датою поступлення (новіші спочатку)
    query = query.order_by(Patient.admission_date.desc())
    
    # Пагінація
    pagination = query.paginate(page=page, per_page=50, error_out=False)
    patients_list = pagination.items
    
    # Для фільтрів - унікальні значення
    departments = db.session.query(Patient.department).distinct().all()
    doctors = db.session.query(Patient.doctor).distinct().all()
    
    return render_template('patients_list.html', 
                         patients=patients_list, 
                         pagination=pagination,
                         departments=[d[0] for d in departments],
                         doctors=[d[0] for d in doctors])

@patients.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient(
            admission_date=form.admission_date.data,
            discharge_date=form.discharge_date.data,
            full_name=form.full_name.data,
            department=form.department.data,
            doctor=form.doctor.data,
            history_number=form.history_number.data,
            comment=form.comment.data,
            is_deceased=form.is_deceased.data,
            death_date=form.death_date.data if form.is_deceased.data else None,  # ОНОВЛЕНО
            created_by=current_user.id
        )
        db.session.add(patient)
        db.session.commit()
        flash('Пацієнта успішно додано!', 'success')
        return redirect(url_for('patients.index'))
    
    return render_template('patient_form.html', form=form, title='Додати пацієнта')

@patients.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    patient = Patient.query.get_or_404(id)
    form = PatientForm(original_history_number=patient.history_number)
    
    if form.validate_on_submit():
        patient.admission_date = form.admission_date.data
        patient.discharge_date = form.discharge_date.data
        patient.full_name = form.full_name.data
        patient.department = form.department.data
        patient.doctor = form.doctor.data
        patient.history_number = form.history_number.data
        patient.comment = form.comment.data
        patient.is_deceased = form.is_deceased.data
        patient.death_date = form.death_date.data if form.is_deceased.data else None  # ОНОВЛЕНО
        patient.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Дані пацієнта оновлено!', 'success')
        return redirect(url_for('patients.index'))
    
    elif request.method == 'GET':
        form.admission_date.data = patient.admission_date
        form.discharge_date.data = patient.discharge_date
        form.full_name.data = patient.full_name
        form.department.data = patient.department
        form.doctor.data = patient.doctor
        form.history_number.data = patient.history_number
        form.comment.data = patient.comment
        form.is_deceased.data = patient.is_deceased
        form.death_date.data = patient.death_date  # ОНОВЛЕНО
    
    return render_template('patient_form.html', form=form, title='Редагувати пацієнта')

@patients.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    flash('Пацієнта видалено!', 'success')
    return redirect(url_for('patients.index'))