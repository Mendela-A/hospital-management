from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField, SelectField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
from app.models import User, Patient
from datetime import datetime

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
    month = SelectField(
        'Місяць',
        choices=[
            (1, 'Січень'), (2, 'Лютий'), (3, 'Березень'), (4, 'Квітень'),
            (5, 'Травень'), (6, 'Червень'), (7, 'Липень'), (8, 'Серпень'),
            (9, 'Вересень'), (10, 'Жовтень'), (11, 'Листопад'), (12, 'Грудень')
        ],
        coerce=int,
        validators=[DataRequired()]
    )
    year = IntegerField(
        'Рік',
        validators=[
            DataRequired(),
            NumberRange(min=2020, max=2030, message='Рік має бути між 2020 та 2030')
        ]
    )
    submit = SubmitField('Експортувати')
    
    def __init__(self, *args, **kwargs):
        super(ExportForm, self).__init__(*args, **kwargs)
        # Встановлення поточного місяця та року за замовчуванням
        if not self.month.data:
            self.month.data = datetime.now().month
        if not self.year.data:
            self.year.data = datetime.now().year