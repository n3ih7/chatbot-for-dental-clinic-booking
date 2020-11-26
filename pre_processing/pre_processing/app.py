import random
import secrets
import time
from flask import jsonify, request, make_response, Flask
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class CHAT_PROGRESS(db.Model):
    __tablename__ = 'CHAT_PROGRESS'
    uid = db.Column('uid', db.INTEGER, primary_key=True)
    token = db.Column('token', db.Text)
    progress = db.Column('progress', db.INTEGER)
    chosen_doctor = db.Column('chosen_doctor', db.INTEGER)
    chosen_timeslot = db.Column('chosen_timeslot', db.Text)


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


def intent_determination(text):
    try:
        response = requests.get(
            url="https://api.wit.ai/message",
            params={
                'q': text
            },
            headers={
                'Authorization': "Bearer PX6UEPURDJN5YZPTSSY6M3X6ZGWT4PVD"
            }, timeout=2
        )
        resp_dict = response.json()
        try:
            if resp_dict["intents"][0]["name"] == 'wit_greetings':
                return 1, None, None
            if resp_dict["intents"][0]["name"] == 'cs9322_list':
                return 2, None, None

            if resp_dict["intents"][0]["name"] == 'cs9322_doctorname':
                if "wit$datetime:datetime" not in resp_dict["entities"] \
                        and "wit$contact:contact" in resp_dict["entities"]:
                    try:
                        name = resp_dict["entities"]["wit$contact:contact"][0]["value"]
                        if name:
                            print("31")
                            return 31, name, None
                        else:
                            return 400, None, None
                    except:
                        return 400, None, None
                if "wit$datetime:datetime" in resp_dict["entities"] \
                        and "wit$contact:contact" not in resp_dict["entities"]:
                    try:
                        t = resp_dict["entities"]["wit$datetime:datetime"][0]["value"]
                        if t:
                            print("32")
                            return 32, None, t
                        else:
                            return 400, None, None
                    except:
                        return 400, None, None
                if "wit$datetime:datetime" in resp_dict["entities"] \
                        and "wit$contact:contact" in resp_dict["entities"]:
                    try:
                        name = resp_dict["entities"]["wit$contact:contact"][0]["value"]
                        t = resp_dict["entities"]["wit$datetime:datetime"][0]["value"]
                        if t:
                            print("33")
                            return 33, name, t
                        else:
                            return 400, None, None
                    except:
                        return 400, None, None
            return 400, None, None
        except:
            return 400, None, None
    except requests.exceptions.RequestException:
        return 599, None, None


@app.route('/ask', methods=['POST'])
def ask_n_response():
    jsonContent = request.get_json()
    session = request.cookies.get("session")

    if not jsonContent['msg']:
        return jsonify(error="No text received", timestamp=str(int(time.time())) + '000'), 400
    elif jsonContent['msg'] and jsonContent['msg_source'] == "user":
        if jsonContent['msg'] == "Y" or jsonContent['msg'] == "y":
            if session is None:
                msg = "Sorry, I don't get it. Please try again."
                response = make_response(
                    jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                tk = str(secrets.token_hex(32))
                response.set_cookie(key='session', value=tk, httponly=True)
                n = CHAT_PROGRESS(token=tk, progress=1)
                db.session.add(n)
                db.session.commit()
                return response
            else:
                u = CHAT_PROGRESS.query.filter_by(token=session).first()
                if u and u.progress == 33:
                    url = "http://timeslot_service:5002/timeslot"
                    payload = {
                        'token': session,
                        'dentist_id': u.chosen_doctor,
                        'timeslot': u.chosen_timeslot,
                        'status_flag': 1
                    }
                    r = requests.post(url, json=payload)
                    jsonContent = r.json()
                    if r.status_code == 409:
                        if jsonContent['error'] == "You cannot make the same booking.":
                            msg = jsonContent['error'] + " Please try again."
                            u.progress = 1
                            db.session.merge(u)
                            db.session.commit()
                        elif jsonContent['error'] == "You can only have one booking at the same time.":
                            msg = jsonContent['error']
                            u.progress = 1
                            db.session.merge(u)
                            db.session.commit()
                        else:
                            url = "http://dentist_service:5001/dentists/id/" + str(u.chosen_doctor)
                            response = requests.get(url=url, timeout=2)
                            resp_dict = response.json()
                            doctor_name = resp_dict["name"].split(' ')[1]
                            msg_1 = jsonContent['error'] + " Please try another time. Here are the available " \
                                                           "time on the same day for Dr " + doctor_name + ":<br/><br/>"
                            msg_2 = ''
                            for x in jsonContent['available_timeslot']:
                                msg_2 = msg_2 + x + "<br/>"
                            msg = msg_1 + msg_2
                        response = make_response(
                            jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                        return response
                    elif r.status_code == 200:
                        msg = "You've successfully booked. <br/><br/>Say 'check appointment' " \
                              "if you change mind or need to check appointment status."
                        response = make_response(
                            jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                        u.progress = 1
                        db.session.merge(u)
                        db.session.commit()
                        return response
                else:
                    msg = "Sorry, I don't get it. Please try again."
                    response = make_response(
                        jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                    tk = str(secrets.token_hex(32))
                    response.set_cookie(key='session', value=tk, httponly=True)
                    n = CHAT_PROGRESS(token=tk, progress=1)
                    db.session.add(n)
                    db.session.commit()
                    return response
        elif jsonContent['msg'] == 'check appointment':
            url = "http://timeslot_service:5002/booking"
            headers = {'Authorization': 'session ' + session}
            r = requests.get(url, headers=headers)
            jsonContent = r.json()
            if r.status_code == 404:
                msg = jsonContent['error']
                response = make_response(
                    jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                return response
            elif r.status_code == 200:
                msg = ''
                for i in jsonContent['msg']:
                    msg += i
                msg += "<br/>Please reply 'CANCEL' to confirm the appointment cancellation if you have any."
                response = make_response(
                    jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                return response
        elif jsonContent['msg'] == 'CANCEL' or jsonContent['msg'] == 'cancel':
            url = "http://timeslot_service:5002/booking"
            headers = {'Authorization': 'session ' + session}
            r = requests.put(url, headers=headers)
            jsonContent = r.json()
            if r.status_code == 404:
                msg = jsonContent['error']
                response = make_response(
                    jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                return response
            elif r.status_code == 200:
                msg = jsonContent['msg']
                response = make_response(
                    jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                return response

        else:
            a, b, c = intent_determination(jsonContent['msg'])
            if a == 599:
                return jsonify(error="Network error", timestamp=str(int(time.time())) + '000'), 599
            elif a == 400:
                msg = "Sorry, I don't get it. Please try again."
                response = make_response(
                    jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)

                if session is None:
                    tk = str(secrets.token_hex(32))
                    response.set_cookie(key='session', value=tk, httponly=True)
                    n = CHAT_PROGRESS(token=tk, progress=1)
                    db.session.add(n)
                    db.session.commit()
                else:
                    u = CHAT_PROGRESS.query.filter_by(token=session).first()
                    if not u:
                        tk = str(secrets.token_hex(32))
                        response.set_cookie(key='session', value=tk, httponly=True)
                        n = CHAT_PROGRESS(token=tk, progress=1)
                        db.session.add(n)
                        db.session.commit()
                return response

            elif a == 1:
                msg_return = [
                    "Hello, welcome to our newly designed online dental booking system. "
                    "We'll start with the information about our dentists with excellent technique. "
                    "<br/><br/>Please say 'dentists' to continue",
                    "Hi, it's glad to see you. Welcome to our newly designed online dental booking system. "
                    "We'll start with the information about our dentists with excellent technique. "
                    "<br/><br/>Please say 'dentists' to continue",
                    "Hi, nice to meet you. welcome to our newly designed online dental booking system. "
                    "We'll start with the information about our dentists with excellent technique. "
                    "<br/><br/>Please say 'dentists' to continue",
                    "I'm good. How are you? welcome to our newly designed online dental booking system. "
                    "We'll start with the information about our dentists with excellent technique. "
                    "<br/><br/>Please say 'dentists' to continue",
                ]
                msg = random.choice(msg_return)
                response = make_response(
                    jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                if session is None:
                    tk = str(secrets.token_hex(32))
                    response.set_cookie(key='session', value=tk, httponly=True)
                    n = CHAT_PROGRESS(token=tk, progress=1)
                    db.session.add(n)
                    db.session.commit()
                else:
                    u = CHAT_PROGRESS.query.filter_by(token=session).first()
                    if u:
                        u.progress = 1
                        db.session.merge(u)
                        db.session.commit()
                    else:
                        tk = str(secrets.token_hex(32))
                        response.set_cookie(key='session', value=tk, httponly=True)
                        n = CHAT_PROGRESS(token=tk, progress=1)
                        db.session.add(n)
                        db.session.commit()
                return response

            elif a == 2:
                response = requests.get(url="http://dentist_service:5001/dentists", timeout=2)
                resp_dict = response.json()
                msg_1 = "We have " + str(resp_dict["length"]) + " different doctors for you to choose:<br/><br/>"
                msg_2 = ""
                for i in resp_dict["details"]:
                    lastname = i["name"].split(' ')[1]
                    r = "Dr " + lastname + " specialized in " + i["specialization"] + "<br/>"
                    msg_2 += r
                msg_3 = "<br/>Please choose the one you'd like to visit."
                msg = msg_1 + msg_2 + msg_3
                response = make_response(
                    jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                if session is None:
                    tk = str(secrets.token_hex(32))
                    response.set_cookie(key='session', value=tk, httponly=True)
                    n = CHAT_PROGRESS(token=tk, progress=2)
                    db.session.add(n)
                    db.session.commit()
                else:
                    u = CHAT_PROGRESS.query.filter_by(token=session).first()
                    if u:
                        u.progress = 2
                        db.session.merge(u)
                        db.session.commit()
                    else:
                        tk = str(secrets.token_hex(32))
                        response.set_cookie(key='session', value=tk, httponly=True)
                        n = CHAT_PROGRESS(token=tk, progress=2)
                        db.session.add(n)
                        db.session.commit()
                return response

            elif a == 31:
                if b:
                    doctor_name = b
                    if b.startswith('Dr '):
                        doctor_name = b.split(' ')[1]
                    if doctor_name.endswith('.'):
                        doctor_name = doctor_name.split('.')[0]
                else:
                    msg = "Sorry, I don't get it. Please try again."
                    response = make_response(
                        jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                    return response

                url = "http://dentist_service:5001/dentists/name/" + doctor_name
                response = requests.get(url=url, timeout=2)

                if response.status_code == 404:
                    msg = "Sorry, I don't get it. Please try again."
                    response = make_response(
                        jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                    return response

                resp_dict = response.json()
                msg_1 = "Here are the details about Dr " + doctor_name + ":<br/><br/>"
                msg_2 = "Name: " + resp_dict["name"] + "<br/>"
                msg_3 = "Location: " + resp_dict["location"] + "<br/>"
                msg_4 = "Specialization: " + resp_dict["specialization"] + "<br/><br/>"
                msg_5 = "Please tell me your preferred appointment time. "

                url_2 = "http://timeslot_service:5002/timeslot"
                response_2 = requests.get(url=url_2, timeout=2)
                resp_dict_2 = response_2.json()
                msg_6 = resp_dict_2["msg"]

                msg = msg_1 + msg_2 + msg_3 + msg_4 + msg_5 + msg_6
                response = make_response(
                    jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                if session is None:
                    tk = str(secrets.token_hex(32))
                    response.set_cookie(key='session', value=tk, httponly=True)
                    n = CHAT_PROGRESS(token=tk, progress=31, chosen_doctor=int(resp_dict["dentist_id"]))
                    db.session.add(n)
                    db.session.commit()
                else:
                    u = CHAT_PROGRESS.query.filter_by(token=session).first()
                    if u:
                        u.progress = 31
                        u.chosen_doctor = int(resp_dict["dentist_id"])
                        db.session.merge(u)
                        db.session.commit()
                    else:
                        tk = str(secrets.token_hex(32))
                        response.set_cookie(key='session', value=tk, httponly=True)
                        n = CHAT_PROGRESS(token=tk, progress=31, chosen_doctor=int(resp_dict["dentist_id"]))
                        db.session.add(n)
                        db.session.commit()
                return response

            elif a == 32:
                if session is None:
                    response = requests.get(url="http://dentist_service:5001/dentists", timeout=2)
                    resp_dict = response.json()
                    msg_0 = "Hi, you need to select the doctor first.<br/>"
                    msg_1 = "We have " + str(resp_dict["length"]) + " different doctors for you to choose:<br/><br/>"
                    msg_2 = ""
                    for i in resp_dict["details"]:
                        lastname = i["name"].split(' ')[1]
                        r = "Dr " + lastname + " specialized in " + i["specialization"] + "<br/>"
                        msg_2 += r
                    msg_3 = "<br/>Please choose the one you'd like to visit."
                    msg = msg_0 + msg_1 + msg_2 + msg_3
                    tk = str(secrets.token_hex(32))
                    response = make_response(
                        jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                    response.set_cookie(key='session', value=tk, httponly=True)
                    n = CHAT_PROGRESS(token=tk, progress=2, chosen_timeslot=c)
                    db.session.add(n)
                    db.session.commit()
                else:
                    u = CHAT_PROGRESS.query.filter_by(token=session).first()
                    if u and u.chosen_doctor:
                        u.progress = 33
                        u.chosen_timeslot = c
                        db.session.merge(u)
                        db.session.commit()
                        url = "http://dentist_service:5001/dentists/id/" + str(u.chosen_doctor)
                        response = requests.get(url=url, timeout=2)
                        resp_dict = response.json()
                        doctor_name = resp_dict["name"].split(' ')[1]
                        msg_1 = "You're now ready to book with Dr " + doctor_name + " " + \
                                parse_time_format(c) + " session.<br/><br/>"
                        msg_2 = "Please reply 'Y' to confirm the booking or ignore this message if change mind."
                        msg = msg_1 + msg_2
                        response = make_response(
                            jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                    else:
                        response = requests.get(url="http://dentist_service:5001/dentists", timeout=2)
                        resp_dict = response.json()
                        msg_0 = "Hi, you need to select the doctor first.<br/>"
                        msg_1 = "We have " + str(resp_dict["length"]) + \
                                " different doctors for you to choose:<br/><br/>"
                        msg_2 = ""
                        for i in resp_dict["details"]:
                            lastname = i["name"].split(' ')[1]
                            r = "Dr " + lastname + " specialized in " + i["specialization"] + "<br/>"
                            msg_2 += r
                        msg_3 = "<br/>Please choose the one you'd like to visit."
                        msg = msg_0 + msg_1 + msg_2 + msg_3
                        tk = str(secrets.token_hex(32))
                        response = make_response(
                            jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                        response.set_cookie(key='session', value=tk, httponly=True)
                        n = CHAT_PROGRESS(token=tk, progress=2, chosen_timeslot=c)
                        db.session.add(n)
                        db.session.commit()
                return response
            elif a == 33:
                if b:
                    doctor_name = b
                    if b.startswith('Dr '):
                        doctor_name = b.split(' ')[1]
                    if doctor_name.endswith('.'):
                        doctor_name = doctor_name.split('.')[0]
                else:
                    msg = "Sorry, I don't get it. Please try again."
                    response = make_response(
                        jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                    return response

                url = "http://dentist_service:5001/dentists/name/" + doctor_name
                response = requests.get(url=url, timeout=2)
                if response.status_code == 404:
                    msg = "Sorry, I don't get it. Please try again."
                    response = make_response(
                        jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                    return response
                resp_dict = response.json()
                if session is None:
                    url = "http://dentist_service:5001/dentists/id/" + str(resp_dict["dentist_id"])
                    response = requests.get(url=url, timeout=2)
                    resp_dict = response.json()
                    doctor_name = resp_dict["name"].split(' ')[1]
                    msg_1 = "You're now ready to book with Dr " + doctor_name + " " + \
                            parse_time_format(c) + " session.<br/><br/>"
                    msg_2 = "Please reply 'Y' to confirm the booking or ignore this message if change mind."
                    msg = msg_1 + msg_2
                    tk = str(secrets.token_hex(32))
                    response = make_response(
                        jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                    response.set_cookie(key='session', value=tk, httponly=True)
                    n = CHAT_PROGRESS(token=tk,
                                      progress=33,
                                      chosen_doctor=int(resp_dict["dentist_id"]),
                                      chosen_timeslot=c)
                    db.session.add(n)
                    db.session.commit()
                else:
                    u = CHAT_PROGRESS.query.filter_by(token=session).first()
                    if u:
                        u.chosen_timeslot = c
                        u.progress = 33
                        u.chosen_doctor = int(resp_dict["dentist_id"])
                        db.session.merge(u)
                        db.session.commit()
                        url = "http://dentist_service:5001/dentists/id/" + str(resp_dict["dentist_id"])
                        response = requests.get(url=url, timeout=2)
                        resp_dict = response.json()
                        doctor_name = resp_dict["name"].split(' ')[1]
                        msg_1 = "You're now ready to book with Dr " + doctor_name + " " + \
                                parse_time_format(c) + " session.<br/><br/>"
                        msg_2 = "Please reply 'Y' to confirm the booking or ignore this message if change mind."
                        msg = msg_1 + msg_2
                        response = make_response(
                            jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                    else:
                        tk = str(secrets.token_hex(32))
                        n = CHAT_PROGRESS(token=tk,
                                          progress=33,
                                          chosen_doctor=int(resp_dict["dentist_id"]),
                                          chosen_timeslot=c)
                        db.session.add(n)
                        db.session.commit()
                        url = "http://dentist_service:5001/dentists/id/" + str(resp_dict["dentist_id"])
                        response = requests.get(url=url, timeout=2)
                        resp_dict = response.json()
                        doctor_name = resp_dict["name"].split(' ')[1]
                        msg_1 = "You're now ready to book with Dr " + doctor_name + " " + \
                                parse_time_format(c) + " session.<br/><br/>"
                        msg_2 = "Please reply 'Y' to confirm the booking or ignore this message if change mind."
                        msg = msg_1 + msg_2
                        response = make_response(
                            jsonify(msg_source="bot", msg=msg, timestamp=str(int(time.time())) + '000'), 200)
                        response.set_cookie(key='session', value=tk, httponly=True)
                return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
