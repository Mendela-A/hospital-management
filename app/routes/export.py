from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps
import pandas as pd
from io import BytesIO
from app import db
from app.models import Patient
from calendar import month_name

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
    form = ExportForm()
    return render_template('export_form.html', form=form)

@export_bp.route('/download', methods=['POST'])
@login_required
@admin_required
def download():
    form = ExportForm()
    
    if form.validate_on_submit():
        month = form.month.data
        year = form.year.data
        
        # Фільтрація пацієнтів за місяцем і роком
        query = Patient.query.filter(
            db.extract('month', Patient.admission_date) == month,
            db.extract('year', Patient.admission_date) == year
        ).order_by(Patient.admission_date.desc())
        
        patients = query.all()
        
        if not patients:
            flash(f'Дані за {month:02d}.{year} не знайдено.', 'warning')
            return redirect(url_for('export.export_form'))
        
        # Створення DataFrame
        data = []
        for p in patients:
            data.append({
                'Дата поступлення': p.admission_date.strftime('%d.%m.%Y'),
                'Дата виписки': p.discharge_date.strftime('%d.%m.%Y') if p.discharge_date else '',
                'ПІБ': p.full_name,
                'Відділення': p.department,
                'Лікар': p.doctor,
                '№ Історії': p.history_number,
                'Статус': 'Помер' if p.is_deceased else 'Живий',
                'Коментар': p.comment if p.comment else ''
            })
        
        df = pd.DataFrame(data)
        
        # Створення Excel файлу в пам'яті
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Пацієнти')
            
            # Налаштування ширини колонок
            worksheet = writer.sheets['Пацієнти']
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
        
        # Формування назви файлу
        filename = f'patients_{year}_{month:02d}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    flash('Помилка при експорті даних.', 'danger')
    return redirect(url_for('export.export_form'))