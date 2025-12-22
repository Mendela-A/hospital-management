FROM python:3.11-slim

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Робоча директорія
WORKDIR /app

# Копіювання залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду додатку
COPY . .

# Змінні середовища
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Відкриття порту
EXPOSE 5000

# Команда запуску
CMD ["python", "run.py"]