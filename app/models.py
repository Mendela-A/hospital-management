from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patients = db.relationship('Patient', backref='creator', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    admission_date = db.Column(db.Date, nullable=False)
    discharge_date = db.Column(db.Date, nullable=True)
    full_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    doctor = db.Column(db.String(200), nullable=False)
    history_number = db.Column(db.String(50), unique=True, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    is_deceased = db.Column(db.Boolean, default=False)
    death_date = db.Column(db.Date, nullable=True)  # НОВЕ ПОЛЕ
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Patient {self.full_name} - {self.history_number}>'