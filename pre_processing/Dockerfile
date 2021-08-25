FROM python:3.8

LABEL MAINTAINER="zack@nono.fi"

COPY pre_processing /pre

WORKDIR /pre

RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]

# CMD ["python3", "app.py"]