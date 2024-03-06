CELERY_BROKER_URL = 'amqp://localhost:5672'  # URL брокера сообщений (RabbitMQ)
CELERY_RESULT_BACKEND = 'redis://localhost:6379'  # URL хранилища результатов (Redis)
CELERY_ACCEPT_CONTENT = ['application/json']  # Типы контента для задач
CELERY_TASK_SERIALIZER = 'json'  # Сериализатор задач
CELERY_RESULT_SERIALIZER = 'json'  # Сериализатор результатов задач
CELERY_TIMEZONE = 'UTC'  # Часовой пояс задач (по умолчанию UTC)