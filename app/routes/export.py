from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.forms import ExportForm
from app.models import Patient
from app import db
from functools import wraps
from datetime import datetime
import pandas as pd
from io import BytesIO

export_bp = Blueprint('export', __name__, url_prefix='/export')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('У вас немає доступу до цієї сторінки.', 'danger')
            return redirect(url_for('patients.index'))
        return f(*args, **kwargs)
    return decorated_function


@export_bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def export_form():
    """Відображення форми експорту"""
    form = ExportForm()
    
    if form.validate_on_submit():
        # Отримуємо дані з форми
        month = int(form.month.data)
        year = int(form.year.data)
        department = form.department.data.strip() if form.department.data else None
        doctor = form.doctor.data.strip() if form.doctor.data else None
        include_deceased = form.include_deceased.data
        
        # Перенаправляємо на експорт з параметрами
        return redirect(url_for('export.export_data', 
                              month=month, 
                              year=year,
                              department=department,
                              doctor=doctor,
                              include_deceased=include_deceased))
    
    return render_template('export_form.html', form=form)


@export_bp.route('/download')
@login_required
@admin_required
def export_data():
    """Експорт даних пацієнтів в Excel"""
    from flask import request
    
    # Отримуємо параметри з URL
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    department = request.args.get('department', '')
    doctor = request.args.get('doctor', '')
    include_deceased = request.args.get('include_deceased', 'True') == 'True'
    
    # Перевірка обов'язкових параметрів
    if not month or not year:
        flash('Не вказано місяць або рік для експорту.', 'danger')
        return redirect(url_for('export.export_form'))
    
    try:
        # Формуємо запит до бази даних
        query = Patient.query.filter(
            db.extract('month', Patient.admission_date) == month,
            db.extract('year', Patient.admission_date) == year
        )
        
        # Додаткові фільтри
        if department:
            query = query.filter(Patient.department.ilike(f'%{department}%'))
        if doctor:
            query = query.filter(Patient.doctor.ilike(f'%{doctor}%'))
        if not include_deceased:
            query = query.filter(Patient.is_deceased == False)
        
        # Сортування
        query = query.order_by(Patient.admission_date.desc())
        
        # Отримуємо дані
        patients = query.all()
        
        if not patients:
            flash(f'Не знайдено пацієнтів за {month}/{year}.', 'warning')
            return redirect(url_for('export.export_form'))
        
        # Підготовка даних для Excel
        data = []
        for p in patients:
            data.append({
                'Дата поступлення': p.admission_date.strftime('%d.%m.%Y'),
                'Дата виписки': p.discharge_date.strftime('%d.%m.%Y') if p.discharge_date else '',
                'ПІБ': p.full_name,
                'Відділення': p.department,
                'Лікар': p.doctor,
                '№ Історії': p.history_number,
                'Коментар': p.comment or '',
                'Статус': 'Помер' if p.is_deceased else 'Живий',
                'Створено': p.created_at.strftime('%d.%m.%Y %H:%M'),
                'Оновлено': p.updated_at.strftime('%d.%m.%Y %H:%M')
            })
        
        # Створюємо DataFrame
        df = pd.DataFrame(data)
        
        # Створюємо Excel файл
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Пацієнти')
            
            # Отримуємо worksheet для форматування
            worksheet = writer.sheets['Пацієнти']
            
            # Автоматичне налаштування ширини колонок
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Назва файлу
        month_names = [
            'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
            'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'
        ]
        filename = f'Пацієнти_{month_names[month-1]}_{year}.xlsx'
        
        flash(f'Експортовано {len(patients)} пацієнтів.', 'success')
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'Помилка при експорті: {str(e)}', 'danger')
        return redirect(url_for('export.export_form'))