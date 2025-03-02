FROM python:3.12.8-slim-bookworm

# setting env variables for optimised building
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt /app

# installing requirements and removing package cache to save on docker image size
RUN pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip/*

COPY . .

EXPOSE 8000

RUN chmod +x /app/run.sh
CMD ["bash", "run.sh"]