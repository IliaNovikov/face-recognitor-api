FROM python:3.12.1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update
COPY . .
CMD [ "python", "main.py" ]
