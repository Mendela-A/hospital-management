from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
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
    discharge_date = DateField('Дата виписки', validators=[Optional()], format='%Y-%m-%d')
    full_name = StringField('ПІБ', validators=[DataRequired(), Length(max=200)])
    department = StringField('Відділення', validators=[DataRequired(), Length(max=100)])
    doctor = StringField('Лікар', validators=[DataRequired(), Length(max=200)])
    history_number = StringField('№ Історії', validators=[DataRequired(), Length(max=50)])
    comment = TextAreaField('Коментар')
    is_deceased = BooleanField('Пацієнт помер')
    death_date = DateField('Дата смерті', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Зберегти')
    
    def __init__(self, original_history_number=None, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        self.original_history_number = original_history_number
    
    def validate_history_number(self, history_number):
        if history_number.data != self.original_history_number:
            patient = Patient.query.filter_by(history_number=history_number.data).first()
            if patient:
                raise ValidationError('Цей номер історії вже використовується.')
    
    def validate_death_date(self, death_date):
        """Перевірка дати смерті"""
        if self.is_deceased.data and not death_date.data:
            raise ValidationError('Якщо пацієнт помер, вкажіть дату смерті.')
        
        if death_date.data and not self.is_deceased.data:
            raise ValidationError('Якщо вказана дата смерті, позначте "Пацієнт помер".')
        
        if death_date.data:
            if self.admission_date.data and death_date.data < self.admission_date.data:
                raise ValidationError('Дата смерті не може бути раніше дати поступлення.')
            
            if self.discharge_date.data and death_date.data > self.discharge_date.data:
                raise ValidationError('Дата смерті не може бути пізніше дати виписки.')


class ExportForm(FlaskForm):
    """Форма для експорту даних"""
    start_date = DateField('Дата початку', validators=[Optional()], format='%Y-%m-%d')
    end_date = DateField('Дата кінця', validators=[Optional()], format='%Y-%m-%d')
    department = StringField('Відділення', validators=[Optional()])
    doctor = StringField('Лікар', validators=[Optional()])
    export_format = SelectField(
        'Формат експорту',
        choices=[('excel', 'Excel (.xlsx)'), ('csv', 'CSV')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Експортувати')