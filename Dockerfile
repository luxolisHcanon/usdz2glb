# FROM python:3.10
# FROM linuxserver/blender:3.5.0
FROM linuxserver/blender:3.5.1

# Fix tzdata asking for "Please select the geographic area in which you live..."
ARG DEBIAN_FRONTEND=noninteractive

RUN apt update && apt-get install git curl -y

# To fix pyzmq build error "g++ not found"
RUN apt install build-essential -y

# Add Redis for Local Queue
# Install dependencies for Redis
RUN apt-get update && apt-get install -y redis-server



RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.5 \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /workdir
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

RUN chmod u+x ./binaries/gltfpack
RUN chmod u+x ./docker_start.sh

ENV PORT=8080

ARG DEVELOPMENT='False'
ENV DEVELOPMENT ${DEVELOPMENT}

ARG GCLOUD_BUCKET='vimage-image-api-io-tmp24h'
ENV GCLOUD_BUCKET ${GCLOUD_BUCKET}

ARG BACKEND_URL
ENV BACKEND_URL ${BACKEND_URL}

EXPOSE ${PORT}

# DEVELOPMENT=False uvicorn main:app --host 0.0.0.0 --port 8090 --reload --log-level debug
# ENTRYPOINT /bin/bash
ENTRYPOINT /workdir/docker_start.sh
# ENTRYPOINT /bin/sh
# CMD uvicorn main:app --host 0.0.0.0 --port 8080 --log-level debug --reload