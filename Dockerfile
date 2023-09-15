FROM python:3.8-alpine3.10

WORKDIR /usr/src/app

# update apk repo
RUN echo "https://dl-4.alpinelinux.org/alpine/v3.10/main" >> /etc/apk/repositories && \
    echo "https://dl-4.alpinelinux.org/alpine/v3.10/community" >> /etc/apk/repositories

# upgrade pip
RUN pip install --upgrade pip

COPY . .

# install requirements
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./script.py"]
CMD ["vandy"]