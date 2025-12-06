import os
import pickle
import time
from concurrent import futures

import grpc
import numpy as np


import model_pb2
import model_pb2_grpc

# Получаем переменные окружения
MODEL_PATH = os.getenv("MODEL_PATH", "./models/model.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v0.0.0")
PORT = os.getenv("PORT", "50051")

# Загрузка модели (для примера создайте модель и сохраните как model.pkl)
try:
    with open(MODEL_PATH, 'rb') as f:
        # В реальном проекте используйте безопасную загрузку
        ML_MODEL = pickle.load(f)
    print(f"✅ Модель успешно загружена из: {MODEL_PATH}")
except Exception as e:
    print(f"❌ Ошибка при загрузке модели: {e}. Используем заглушку.")
    # Заглушка, если модель не найдена (для тестов)
    class DummyModel:
        def predict(self, X):
            # Всегда предсказываем '1'
            return np.array(['1'])
        def predict_proba(self, X):
            # Всегда возвращаем вероятность 92%
            return np.array([[0.08, 0.92]])
    ML_MODEL = DummyModel()


class PredictionService(model_pb2_grpc.PredictionServiceServicer):
    """
    Реализация сервиса предсказаний gRPC.
    """
    def Health(self, request, context):
        """Реализация /health"""
        return model_pb2.HealthResponse(
            status="ok",
            model_version=MODEL_VERSION
        )

    def Predict(self, request, context):
        """Реализация /predict"""
        try:
            # Преобразование входных данных
            features = np.array([request.features], dtype=np.float64)
            
            # Получение предсказания
            prediction_label = ML_MODEL.predict(features)[0]
            # Получение вероятности (confidence)
            # Предполагаем, что model.predict_proba возвращает [вероятность_класса_0, вероятность_класса_1, ...]
            confidence = ML_MODEL.predict_proba(features).max()

            return model_pb2.PredictResponse(
                prediction=str(prediction_label),
                confidence=confidence,
                model_version=MODEL_VERSION
            )

        except Exception as e:
            # Обработка ошибок
            print(f"❌ Ошибка при предсказании: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Prediction error: {e}")
            return model_pb2.PredictResponse()


def serve():
    """Запуск gRPC-сервера."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_pb2_grpc.add_PredictionServiceServicer_to_server(
        PredictionService(), server
    )
    # Начинаем слушать указанный порт
    server.add_insecure_port(f'[::]:{PORT}')
    server.start()
    print(f"🚀 gRPC Server запущен на порту {PORT} с версией модели {MODEL_VERSION}...")
    try:
        while True:
            time.sleep(86400) # Ждем сутки
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    # Эта строка позволяет запускать сервер как `python -m server.server`
    #os.chdir(os.path.dirname(os.path.abspath(__file__)))
    serve()