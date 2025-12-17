from app import create_app, db
from app.models import User, Patient

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Patient': Patient}

def init_db():
    """Ініціалізація бази даних та створення адміністратора"""
    with app.app_context():
        db.create_all()
        
        # Перевірка чи існує адміністратор
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✓ Створено адміністратора: username=admin, password=admin123')
        else:
            print('✓ Адміністратор вже існує')

if __name__ == '__main__':
    init_db()
    print('✓ База даних ініціалізована')
    print('✓ Запуск сервера...')
    print('✓ Відкрийте http://127.0.0.1:5000 у браузері')
    app.run(debug=True)