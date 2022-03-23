FROM selenium/standalone-chrome:99.0.4844.74

RUN sudo apt-get update
RUN sudo apt-get -y install python3 python3-pip

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8881

ENV os linux

CMD [ "python3", "./app.py" ]