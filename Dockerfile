FROM python:3.9
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
COPY . .
# Install MySQL client dependencies
RUN apt-get -y install default-libmysqlclient-dev
RUN pip install -r requirements.txt

