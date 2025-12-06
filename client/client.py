import os
import sys
import grpc


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')

sys.path.append(project_root)

from server import model_pb2
from server import model_pb2_grpc

def run():
    """Локальное тестирование gRPC-сервиса."""
    PORT = os.getenv("PORT", "50051")
    target = f'localhost:{PORT}'
    print(f"✨ Подключение к gRPC-сервису: {target}")

    # Устанавливаем соединение с сервером
    with grpc.insecure_channel(target) as channel:
        stub = model_pb2_grpc.PredictionServiceStub(channel)

        ## 1. Проверка /health
        print("\n--- Проверка /health ---")
        try:
            health_request = model_pb2.HealthRequest()
            health_response = stub.Health(health_request)
            print("✅ Ответ /health:", {
                "status": health_response.status,
                "modelVersion": health_response.model_version
            })
        except grpc.RpcError as e:
            print(f"❌ Ошибка /health: {e.details()}")

        ## 2. Проверка /predict
        print("\n--- Проверка /predict ---")
        try:
            # Пример входных данных для модели (Features)
            predict_request = model_pb2.PredictRequest(features=[1.0, 2.0, 0.5])
            predict_response = stub.Predict(predict_request)
            print("✅ Ответ /predict:", {
                "prediction": predict_response.prediction,
                "confidence": predict_response.confidence,
                "modelVersion": predict_response.model_version
            })
        except grpc.RpcError as e:
            print(f"❌ Ошибка /predict: {e.details()}")

if __name__ == '__main__':
    run()