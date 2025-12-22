from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from datetime import datetime
from app.models import User, Patient

class LoginForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')


class UserForm(FlaskForm):
    username = StringField('Ім\'я користувача', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Роль', choices=[('user', 'Користувач'), ('admin', 'Адміністратор')], validators=[DataRequired()])
    submit = SubmitField('Зберегти')
    
    def __init__(self, original_username=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Це ім\'я користувача вже використовується.')


class PatientForm(FlaskForm):
    admission_date = DateField('Дата поступлення', validators=[DataRequired()], format='%Y-%m-%d')
    discharge_date = DateField('Дата виписки', format='%Y-%m-%d')
    full_name = StringField('ПІБ', validators=[DataRequired(), Length(max=200)])
    department = StringField('Відділення', validators=[DataRequired(), Length(max=100)])
    doctor = StringField('Лікар', validators=[DataRequired(), Length(max=200)])
    history_number = StringField('№ Історії', validators=[DataRequired(), Length(max=50)])
    comment = TextAreaField('Коментар')
    is_deceased = BooleanField('Пацієнт помер')
    submit = SubmitField('Зберегти')
    
    def __init__(self, original_history_number=None, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        self.original_history_number = original_history_number
    
    def validate_history_number(self, history_number):
        if history_number.data != self.original_history_number:
            patient = Patient.query.filter_by(history_number=history_number.data).first()
            if patient:
                raise ValidationError('Цей номер історії вже використовується.')


class ExportForm(FlaskForm):
    """Форма для експорту даних пацієнтів"""
    
    month = SelectField(
        'Місяць', 
        choices=[
            ('01', 'Січень'), ('02', 'Лютий'), ('03', 'Березень'),
            ('04', 'Квітень'), ('05', 'Травень'), ('06', 'Червень'),
            ('07', 'Липень'), ('08', 'Серпень'), ('09', 'Вересень'),
            ('10', 'Жовтень'), ('11', 'Листопад'), ('12', 'Грудень')
        ],
        validators=[DataRequired()],
        default=str(datetime.now().month).zfill(2)
    )
    
    year = SelectField(
        'Рік',
        choices=[
            (str(year), str(year)) 
            for year in range(datetime.now().year - 2, datetime.now().year + 1)
        ],
        validators=[DataRequired()],
        default=str(datetime.now().year)
    )
    
    department = StringField(
        'Відділення (необов\'язково)',
        validators=[Optional(), Length(max=100)]
    )
    
    doctor = StringField(
        'Лікар (необов\'язково)',
        validators=[Optional(), Length(max=200)]
    )
    
    include_deceased = BooleanField(
        'Включити померлих пацієнтів',
        default=True
    )
    
    submit = SubmitField('Експортувати в Excel')