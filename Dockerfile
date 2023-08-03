FROM python:3.10.12-slim

RUN mkdir -p /usr/local/share/ca-certificates/Yandex/   
COPY yandex.crt /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt


RUN pip install \
            --upgrade \
            --extra-index-url https://pull_deploy_token:XxqxVD-oQUQtCR-drW36@gitlab.encm.dev/api/v4/projects/67/packages/pypi/simple \
            "data-wrapper>=2,<3"

COPY requirements.txt requirements.txt
RUN  pip install -r requirements.txt

COPY . .
# WORKDIR /genesis_arena/baseline

# CMD ["python", "insert_baseline_today.py"]

CMD ["./update_baseline.sh"]