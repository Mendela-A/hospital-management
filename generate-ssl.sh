#!/bin/bash

# Скрипт для генерації самопідписного SSL сертифіката

echo "🔐 Генерація SSL сертифіката..."

# Створення директорії для сертифікатів
mkdir -p nginx/ssl

# Генерація приватного ключа та сертифіката
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=UA/ST=Ivano-Frankivsk/L=Perehinske/O=Hospital/OU=IT/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

# Встановлення прав доступу
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem

echo "✅ SSL сертифікат створено успішно!"
echo "📁 Файли:"
echo "   - nginx/ssl/cert.pem (публічний сертифікат)"
echo "   - nginx/ssl/key.pem (приватний ключ)"
echo ""
echo "⚠️  УВАГА: Це самопідписний сертифікат!"
echo "   Браузер покаже попередження про безпеку."
echo "   Для production використовуйте Let's Encrypt."