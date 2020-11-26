from flask import jsonify, Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ds_db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class DENTIST_INFO(db.Model):
    __tablename__ = 'DENTIST_INFO'
    dentist_id = db.Column('dentist_id', db.INTEGER, primary_key=True)
    name = db.Column('name', db.Text)
    location = db.Column('location', db.Text)
    specialization = db.Column('specialization', db.Text)


@app.route('/dentists', methods=['GET'])
def doctor_list():
    a = DENTIST_INFO.query.all()
    if a:
        dentists_list = []
        for i in a:
            dentist_dict = {
                "dentist_id": i.dentist_id,
                "name": i.name,
                "location": i.location,
                "specialization": i.specialization
            }
            dentists_list.append(dentist_dict)
        return jsonify(length=len(dentists_list),
                       details=dentists_list), 200
    else:
        return jsonify(error="We didn't find anything match your search."), 404


@app.route('/dentists/name/<name>', methods=['GET'])
def doctor_info_name(name):
    keyword = "%{}%".format(name)
    a = DENTIST_INFO.query.filter(DENTIST_INFO.name.like(keyword)).first()
    if a:
        return jsonify(dentist_id=a.dentist_id,
                       name=a.name,
                       location=a.location,
                       specialization=a.specialization), 200
    else:
        return jsonify(error="We didn't find anything match your search."), 404


@app.route('/dentists/id/<did>', methods=['GET'])
def doctor_info_id(did):
    a = DENTIST_INFO.query.filter_by(dentist_id=did).first()
    if a:
        return jsonify(dentist_id=a.dentist_id,
                       name=a.name,
                       location=a.location,
                       specialization=a.specialization), 200
    else:
        return jsonify(error="We didn't find anything match your search."), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001', debug=True)
