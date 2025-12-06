# 1. Базовый образ
# Используем python:3.11-slim для минимального размера.
FROM python:3.11-slim

# 2. Переменные окружения
# Они используются в server/server.py
ENV PORT=50051 \
    MODEL_PATH=/app/models/model.pkl \
    MODEL_VERSION=v1.0.0

# 3. Рабочая директория
# Все пути внутри контейнера будут относительны к /app
WORKDIR /app

# 4. Установка зависимостей Python
# Копируем requirements.txt
COPY requirements.txt .
# Устанавливаем зависимости (grpcio, scikit-learn и т.д.)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Генерация gRPC-кода
# Копируем .proto-файл
COPY protos/ protos/
# Создаем целевую папку 'server'
RUN mkdir -p server
# Запускаем компилятор для генерации model_pb2.py и model_pb2_grpc.py в папку server/
RUN python -m grpc_tools.protoc -I./protos --python_out=./server --grpc_python_out=./server ./protos/model.proto

# 6. Копирование остального кода и модели
# Копируем исходный код сервера (server.py, __init__.py), клиента и модель.
# Этот шаг перезаписывает сгенерированные файлы model_pb2.py и model_pb2_grpc.py,
# если они существуют локально в вашей папке server/
COPY server/ server/
COPY client/ client/
COPY models/ models/

# 7. Открываем порт
EXPOSE 50051

# 8. Команда запуска
# Запускаем сервер как пакет/модуль Python.
CMD ["python", "server/server.py"]