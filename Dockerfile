FROM python:3.11-slim

# ВАЖНО: Эта строка включает отображение логов в реальном времени
ENV PYTHONUNBUFFERED=1

# Рабочая папка должна совпадать с той, что в docker-compose (/src)
WORKDIR /src

# Копируем зависимости и устанавливаем их
COPY requirements.txt /src/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . /src/

# Команда запуска
CMD ["python", "run.py"]
