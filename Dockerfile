FROM python:3.14.5-slim
WORKDIR /usr/local/app

ENV DB_LOCATION=sqlite:////data/database.db
ENV LOG_LOCATION=/data/graggle_bot.log

RUN pip install uv

COPY uv.lock pyproject.toml README.md ./
RUN uv sync

COPY src/ ./src/

RUN mkdir /data

RUN adduser pycord
RUN chown -R pycord:pycord /usr/local/app
RUN chown -R pycord:pycord /data

USER pycord

CMD ["uv", "run", "graggle-bot"]