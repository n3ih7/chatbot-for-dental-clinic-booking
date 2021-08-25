FROM python:3.8

LABEL MAINTAINER="zack@nono.fi"

COPY dentist_service /d_s

WORKDIR /d_s

RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "1", "--bind", "0.0.0.0:5001", "app:app"]

# CMD ["python3", "app.py"]