FROM python:3.10.12-slim

# Create directory for Yandex ca-certificate
RUN mkdir -p /usr/local/share/ca-certificates/Yandex/   
COPY yandex.crt /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt

# Install a custom-written library data_wrapper
# You need to use an environment variable while building docker: --build-arg url_wrapper=$DATA_WRAPPER_URL
ARG url_wrapper
ENV DATA_WRAPPER_URL $url_wrapper
RUN pip install --upgrade --extra-index-url $DATA_WRAPPER_URL "data-wrapper>=2,<3"

# Install libraries
COPY requirements.txt requirements.txt
RUN  pip install -r requirements.txt

# Copy full project in visibility area docker
COPY . .
# Set the working directory
WORKDIR /genesis_arena/baseline

CMD ["python", "insert_baseline_today.py"]