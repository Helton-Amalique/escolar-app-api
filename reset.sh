#!/bin/bash

echo "🔄 Resetando migrações e banco de dados..."

# 1. Apagar migrações antigas (exceto __init__.py)
find ./ -path "*/migrations/*.py" ! -name "__init__.py" -delete
find ./ -path "*/migrations/*.pyc" -delete

# 2. Resetar banco de dados Postgres dentro do container
# Ajuste o nome do banco e usuário conforme seu settings.py
DB_NAME="escolar-app-api"
DB_USER="postgres"
DB_CONTAINER="escolar-app-api-db-1"

echo "🗑️ Dropando banco $DB_NAME..."
docker exec -it $DB_CONTAINER psql -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"
echo "📦 Criando banco $DB_NAME..."
docker exec -it $DB_CONTAINER psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

# 3. Criar novas migrações
docker exec -it escolar-app-api-1 python manage.py makemigrations

# 4. Aplicar migrações
docker exec -it escolar-app-api-1 python manage.py migrate --fake-initial

# 5. Criar superusuário novamente
docker exec -it escolar-app-api-1 python manage.py createsuperuser

echo "✅ Reset concluído! Banco e migrações sincronizados."

