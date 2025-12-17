import pandas as pd
from datetime import datetime
from app import create_app, db
from app.models import Patient, User

def import_patients_from_excel(excel_file_path, created_by_username='admin'):
    """
    Імпорт пацієнтів з Excel файлу
    
    Args:
        excel_file_path: шлях до Excel файлу
        created_by_username: ім'я користувача, який створює записи (за замовчуванням 'admin')
    """
    app = create_app()
    
    with app.app_context():
        # Знайти користувача
        user = User.query.filter_by(username=created_by_username).first()
        if not user:
            print(f"❌ Користувача '{created_by_username}' не знайдено!")
            print("Створіть користувача або вкажіть існуюче ім'я.")
            return
        
        try:
            # Читання Excel файлу
            print(f"📂 Читання файлу: {excel_file_path}")
            df = pd.read_excel(excel_file_path)
            
            # Виведення назв колонок для перевірки
            print(f"📋 Знайдені колонки: {list(df.columns)}")
            
            # Очищення назв колонок (видалення пробілів)
            df.columns = df.columns.str.strip()
            
            # Підрахунок
            total = len(df)
            success = 0
            errors = 0
            skipped = 0
            
            print(f"\n📊 Знайдено {total} записів у файлі")
            print("⏳ Починаю імпорт...\n")
            
            for index, row in df.iterrows():
                try:
                    # Перевірка обов'язкових полів
                    if pd.isna(row['ПІБ']) or pd.isna(row['№ Історії']):
                        print(f"⚠️  Рядок {index + 2}: Пропущено (відсутні ПІБ або № Історії)")
                        skipped += 1
                        continue
                    
                    # Перевірка чи існує пацієнт з таким номером історії
                    existing = Patient.query.filter_by(history_number=str(row['№ Історії']).strip()).first()
                    if existing:
                        print(f"⚠️  Рядок {index + 2}: Пропущено (№ Історії {row['№ Історії']} вже існує)")
                        skipped += 1
                        continue
                    
                    # Обробка дати виписки
                    discharge_date = None
                    if not pd.isna(row['ДАТА']):
                        if isinstance(row['ДАТА'], datetime):
                            discharge_date = row['ДАТА'].date()
                        elif isinstance(row['ДАТА'], str):
                            try:
                                discharge_date = datetime.strptime(row['ДАТА'], '%d.%m.%Y').date()
                            except ValueError:
                                try:
                                    discharge_date = datetime.strptime(row['ДАТА'], '%Y-%m-%d').date()
                                except ValueError:
                                    print(f"⚠️  Рядок {index + 2}: Неправильний формат дати '{row['ДАТА']}'")
                    
                    # Створення запису пацієнта
                    patient = Patient(
                        admission_date=discharge_date or datetime.now().date(),  # Якщо немає дати виписки, ставимо поточну
                        discharge_date=discharge_date,
                        full_name=str(row['ПІБ']).strip(),
                        department=str(row['ВІДДІЛЕННЯ']).strip() if not pd.isna(row['ВІДДІЛЕННЯ']) else 'Не вказано',
                        doctor=str(row['ЛІКАР']).strip() if not pd.isna(row['ЛІКАР']) else 'Не вказано',
                        history_number=str(row['№ Історії']).strip(),
                        comment=str(row['Коментар']).strip() if not pd.isna(row['Коментар']) else None,
                        is_deceased=False,
                        created_by=user.id
                    )
                    
                    db.session.add(patient)
                    success += 1
                    print(f"✓ Рядок {index + 2}: {patient.full_name} - успішно додано")
                    
                except Exception as e:
                    errors += 1
                    print(f"❌ Рядок {index + 2}: Помилка - {str(e)}")
                    continue
            
            # Збереження змін
            db.session.commit()
            
            # Підсумок
            print("\n" + "="*50)
            print("📊 РЕЗУЛЬТАТИ ІМПОРТУ:")
            print(f"✓ Успішно додано: {success}")
            print(f"⚠️  Пропущено: {skipped}")
            print(f"❌ Помилок: {errors}")
            print(f"📋 Всього оброблено: {total}")
            print("="*50)
            
        except FileNotFoundError:
            print(f"❌ Файл не знайдено: {excel_file_path}")
        except Exception as e:
            print(f"❌ Критична помилка: {str(e)}")
            db.session.rollback()


if __name__ == '__main__':
    # Використання:
    # 1. Покладіть ваш Excel файл у папку проєкту
    # 2. Вкажіть правильну назву файлу нижче
    # 3. Запустіть: python import_from_excel.py
    
    excel_file = 'patients.xlsx'  # ← Змініть на назву вашого файлу
    
    print("🏥 ІМПОРТ ПАЦІЄНТІВ З EXCEL")
    print("="*50)
    
    import_patients_from_excel(excel_file, created_by_username='admin')
    
    print("\n✅ Імпорт завершено!")
    print("💡 Тепер можете запустити додаток: python run.py")