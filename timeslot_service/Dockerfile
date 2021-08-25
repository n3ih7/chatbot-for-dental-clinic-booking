FROM python:3.8

LABEL MAINTAINER="zack@nono.fi"

COPY timeslot_service /t_s

WORKDIR /t_s

RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "1", "--bind", "0.0.0.0:5002", "app:app"]

# CMD ["python3", "app.py"]