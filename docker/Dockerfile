FROM python:3.9.10-buster

COPY Pipfile.lock Pipfile /

RUN apt-get update && apt-get install -y \
           python3-pygresql  \
    && pip install --upgrade pip==21.1.1 packaging==20.9 setuptools==56.2.0 pipenv==2020.11.15 \
    && pipenv install --deploy --system --ignore-pipfile \
    && rm -rf .cache/pip

COPY docker/entrypoint.sh /

ENV PYTHONUNBUFFERED=1
ENV DJANGO_DATABASE=sqlite

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["run"]

WORKDIR /code
COPY . /code/
RUN ./manage.py collectstatic -l --noinput
