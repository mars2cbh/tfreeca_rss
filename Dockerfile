FROM python:3-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8881

ENV os linux

CMD [ "python", "./app.py" ]