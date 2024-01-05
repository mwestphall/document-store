FROM python:3.12

WORKDIR /src/
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ /src/

CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8089" ]
