FROM python:3.10.7-alpine3.16 as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev alpine-sdk && \
    pip3 install --prefix=/install -r /requirements.txt

# Can clean up a lot of space by deleting rogue .c files etc
# Cleaning up __pycache__ gains more space
RUN find /install/lib/python3.10 -name '*.c' -delete && \
    find /install/lib/python3.10 -name '*.pxd' -delete && \
    find /install/lib/python3.10 -name '*.pyd' -delete && \
    find /install/lib/python3.10 -name '__pycache__' | xargs rm -r

FROM python:3.10.7-alpine3.16

COPY --from=builder /install /usr/local
COPY asst/ /asst

WORKDIR /asst
EXPOSE 5000

ENTRYPOINT ["python3", "main.py"]
