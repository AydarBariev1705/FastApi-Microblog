FROM python:3.11

COPY requirements.txt /main/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /main/requirements.txt

COPY . /app
WORKDIR /app

CMD ["uvicorn", "main.app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]