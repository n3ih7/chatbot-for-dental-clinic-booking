import requests
from flask import jsonify, Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ts_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def parse_time_format(s):
    s_list = s[:-10].split("T")
    yr = s_list[0].split("-")[0]
    month = s_list[0].split("-")[1]
    day = s_list[0].split("-")[2]
    clock = s_list[1].split(":")[0]
    if int(clock) < 11:
        clock = str(int(clock) % 12) + "AM-" + str(int(clock) % 12 + 1) + "AM"
    elif int(clock) == 11:
        clock = "11AM-12PM"
    elif int(clock) == 12:
        clock = "12PM-1PM"
    else:
        clock = str((int(clock) - 12) % 12) + "PM-" + str((int(clock) - 12) % 12 + 1) + "PM"
    r = day + "/" + month + "/" + yr + " " + clock
    return r


class TIMESLOT_SERVICE(db.Model):
    __tablename__ = 'TIMESLOT_SERVICE'
    booking_id = db.Column('booking_id', db.INTEGER, primary_key=True)
    token = db.Column('token', db.Text)
    dentist_id = db.Column('dentist_id', db.INTEGER)
    timeslot = db.Column('timeslot', db.Text)
    status_flag = db.Column('status_flag', db.INTEGER)


@app.route('/timeslot', methods=['GET', 'POST'])
def timeslot():
    if request.method == 'GET':
        return jsonify(msg="Usually, our dentists are available "
                           "for one-hour appointment from 9:00 AM to 5:00 PM every day"), 200
    elif request.method == 'POST':
        jsonContent = request.get_json()

        token = jsonContent["token"]
        dentist_id = jsonContent["dentist_id"]
        ts = jsonContent["timeslot"]

        cc = TIMESLOT_SERVICE.query.filter_by(token=token, status_flag=1).all()
        if len(cc) > 0:
            return jsonify(error="You can only have one booking at the same time. <br/><br/>Say 'check appointment' "
                                 "if you need to check appointment status."), 409

        check = TIMESLOT_SERVICE.query.filter_by(dentist_id=dentist_id, timeslot=ts, status_flag=1).first()
        if check:
            if check.token == token:
                return jsonify(error="You cannot make the same booking. <br/><br/>Say 'check appointment' "
                                     "if you need to check appointment status."), 409
            else:
                available_timeslot = []
                for t in range(9, 17):
                    ts_1 = ts[:11]
                    ts_3 = ts[13:]
                    ts_2 = str(t)
                    if len(ts_2) == 1:
                        ts_2 = '0' + ts_2
                    search_t = ts_1 + ts_2 + ts_3
                    cc = TIMESLOT_SERVICE.query.filter_by(dentist_id=dentist_id,
                                                          timeslot=search_t,
                                                          status_flag=1).first()
                    if not cc:
                        available_timeslot.append(parse_time_format(search_t))
                return jsonify(error="This timeslot has been taken.",
                               available_timeslot=available_timeslot), 409
        else:
            a = TIMESLOT_SERVICE(token=token,
                                 dentist_id=dentist_id,
                                 timeslot=ts,
                                 status_flag=jsonContent["status_flag"])
            db.session.add(a)
            db.session.commit()
            return jsonify(msg="success"), 200


@app.route('/booking', methods=['GET', 'PUT'])
def booking():
    if request.method == 'GET':
        if request.headers['Authorization'] and request.headers['Authorization'].startswith('session '):
            session = request.headers['Authorization'][8:]
            check = TIMESLOT_SERVICE.query.filter_by(token=session).all()
            if check:
                msg = []
                for i in check:
                    url = "http://dentist_service:5001/dentists/id/" + str(i.dentist_id)
                    response = requests.get(url=url, timeout=2)
                    resp_dict = response.json()
                    doctor_name = resp_dict["name"].split(' ')[1]
                    msg_1 = "You have an appointment with Dr " + doctor_name + " " + parse_time_format(i.timeslot) + \
                            ".<br/>"
                    if i.status_flag == 0:
                        msg_2 = " (CANCELLED)<br/>"
                        msg_1 = msg_1.rstrip("<br/>")
                        msg_1 += msg_2
                    msg.append(msg_1)
                print(msg)
                return jsonify(msg=msg), 200
            else:
                return jsonify(error="You don't have any available appointment."), 404
        else:
            return jsonify(error="You don't have any available appointment."), 404

    if request.method == 'PUT':
        if request.headers['Authorization'] and request.headers['Authorization'].startswith('session '):
            session = request.headers['Authorization'][8:]
            check = TIMESLOT_SERVICE.query.filter_by(token=session, status_flag=1).first()
            if check:
                check.status_flag = 0
                db.session.merge(check)
                db.session.commit()
                return jsonify(msg="Your appointment has been cancelled. <br/><br/>Say 'check appointment' "
                                   "if need to check appointment status."), 200
            else:
                return jsonify(error="You don't have any available appointment."), 404
        else:
            return jsonify(error="You don't have any available appointment."), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002', debug=True)
