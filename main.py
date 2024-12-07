# from sqlalchemy import text
from sqlalchemy.orm import Session
from flask import Flask, jsonify, render_template, request, redirect, url_for

from database.engine import get_engine
from datetime import datetime, time
import database.querys as querys

app = Flask(__name__)

admin = '1111'
# user = None


def create_session():
    return Session(get_engine())


@app.route('/logout')
def logout():
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        global user
        login = request.form.get('login')
        password = request.form.get('password')
    if login == 'admin':
        if password == admin:  # Предполагается, что переменная admin_password определена
            user = 'admin'
            return redirect(url_for('get_list_appointments'))
        else:
            error_message = "Неверный пароль для администратора, попробуйте ещё раз"
            return redirect(url_for('error_page', message=error_message))
    else:
        with create_session() as session:
            temp = querys.get_user_from_db(session, polis=login)
            if temp:
                if temp.password == password:
                    user = temp
                    return redirect(url_for('get_list_appointments'))
                else:
                    error_message = "Неверный пароль, попробуйте ещё раз"
                    return redirect(url_for('error_page', message=error_message))
            else:
                error_message = """Такого пациента нет в базе!<br><br>
                                Для регистрации обратитесь к администратору"""
                return redirect(url_for('error_page', message=error_message))



@app.route('/appointments', methods=['GET'])
def get_list_appointments():
    with create_session() as session:
        headers_schedule, contact_headers_schedule, schedule, contact_schedule = querys.get_schedule(session)
        headers_appointments, appointments = querys.get_appointments(session)
        _, doctors = querys.get_list_doctors(session)
        _, patients = querys.get_patients(session)
        _, services = querys.get_services(session)
        # appointments = []
        if user != 'admin':
            temp = []
            for appointment in appointments:
                if appointment.get('polis') == user.polis:
                    temp.append(appointment)
            appointments = temp

        data = dict(user=user, headers_schedule=headers_schedule,
                    contact_headers_schedule=contact_headers_schedule,
                    schedule=schedule, contact_schedule=contact_schedule,
                    headers_appointments=headers_appointments,
                    appointments=appointments,
                    doctors=doctors, patients=patients, services=services)

    return render_template('appointments.html', **data)


@app.route('/appointments/new', methods=['POST'])
def insert_appointments():
    with create_session() as session:
        try:
            data = request.form.to_dict()
            querys.add_appointments(session, **data)
            return redirect(url_for('get_list_appointments'))
        except Exception as e:
            error_message = str(e)
            return redirect(url_for('error_page', message=error_message))


@app.route('/appointments/delete/<int:id_appointment>', methods=['POST'])
def delete_appointment(id_appointment: int):
    with create_session() as session:
        querys.delete_appointment(session, id_appointment)
        return redirect(url_for('get_list_appointments'))


@app.route('/appointments/add_service_to_appointment/<int:id_appointment>/<int:d_id>', methods=['GET'])
def add_service_form(id_appointment: int, d_id: int):
    try:
        with create_session() as session:
            _, appointments = querys.get_appointments(session)
            appointment = next((a for a in appointments if a.get('id_appointment') == id_appointment), None)
            if not appointment:
                raise Exception("Назначение не найдено")
            services = querys.get_service_special_doctor(session, d_id)
            if not services:
                raise Exception("У данного врача нет услуг для записи")
        return render_template('add_service.html', a=appointment, services=services)
    except Exception as e:
        error_message = str(e)
        return redirect(url_for('error_page', message=error_message))


@app.route('/appointments_services/new', methods=['POST'])
def insert_appointment_service_route():
    with create_session() as session:
        try:
            data = request.form.to_dict()
            id_appointment = data.get('id_appointment')
            id_service = data.get('id_service')
            print(id_appointment)
            print(id_service)
            querys.insert_appointment_service(session, int(id_appointment), int(id_service))
            return redirect(url_for('get_list_appointments'))
        except Exception:
            return redirect(url_for('get_list_appointments'))


def get_doctors_list(session):
    return session.query(doctors).all()


@app.route('/patients', methods=['GET'])
def get_list_patiens():
    with create_session() as session:
        headers_schedule, contact_headers_schedule, schedule, contact_schedule = querys.get_schedule(session)
        headers_patient, patients = querys.get_patients(session)

        data = dict(user=user, headers_schedule=headers_schedule,
                    contact_headers_schedule=contact_headers_schedule,
                    schedule=schedule, contact_schedule=contact_schedule,
                    headers_patient=headers_patient, patients=patients)

        return render_template('patients.html', **data)


@app.route('/patients/delete/<string:polis>', methods=['GET'])
def delete_patient(polis: str):
    with create_session() as session:
        querys.delete_patients(session, polis)
        return redirect(url_for('get_list_patiens'))


@app.route('/patients/new', methods=['GET', 'POST'])
def card_patient():
    if request.method == 'GET':
        return render_template('new_patient.html')
    elif request.method == 'POST':
        data = request.form.to_dict()
        with create_session() as session:
            try:
                querys.add_patients(session, data)
            except Exception as e:
                error_message = e.args[0]
                return redirect(url_for('error_page', message=error_message))
            return redirect(url_for('get_list_patiens'))


@app.route('/patients_without_appointments', methods=['GET'])
def get_patients_without_appointments_view():
    with create_session() as session:
        headers_schedule, contact_headers_schedule, schedule, contact_schedule = querys.get_schedule(session)
        headers_patient, patients = querys.get_patients_without_appointments(session)

        data = dict(user=user, headers_schedule=headers_schedule,
                    contact_headers_schedule=contact_headers_schedule,
                    schedule=schedule, contact_schedule=contact_schedule,
                    headers_patient=headers_patient, patients=patients)
        print(data)
        return render_template('patients_without_appointments.html', **data)


@app.route('/doctors', methods=['GET'])
def get_list_doctors():
    with create_session() as session:
        headers_schedule, contact_headers_schedule, schedule, contact_schedule = querys.get_schedule(session)
        headers_doctor, doctors = querys.get_list_doctors(session)

        data = dict(user=user, headers_schedule=headers_schedule,
                    contact_headers_schedule=contact_headers_schedule,
                    schedule=schedule, contact_schedule=contact_schedule,
                    headers_doctor=headers_doctor, doctors=doctors)

        return render_template('doctors.html', **data)


@app.route('/doctors/delete/<int:office>', methods=['GET'])
def delete_doctor(office: int):
    with create_session() as session:
        querys.delete_doctor(session, office)
        return redirect(url_for('get_list_doctors'))


@app.route('/doctors/new', methods=['GET', 'POST'])
def new_doctor():
    if request.method == 'GET':
        return render_template('new_doctor.html')
    elif request.method == 'POST':
        data = request.form.to_dict()
        with create_session() as session:
            try:
                querys.add_doctor(session, data)
            except Exception as e:
                error_message = e.args[0]
                return redirect(url_for('error_page', message=error_message))
            return redirect(url_for('get_list_doctors'))


@app.route('/services', methods=['GET'])
def get_list_services():
    with create_session() as session:
        headers_schedule, contact_headers_schedule, schedule, contact_schedule = querys.get_schedule(session)
        headers_service, services = querys.get_services(session)
        headers_doctors, doctors = querys.get_list_doctors(session)

        total_cost = querys.get_total_cost(session)

        data = dict(user=user, headers_schedule=headers_schedule,
                    contact_headers_schedule=contact_headers_schedule,
                    schedule=schedule, contact_schedule=contact_schedule,
                    headers_service=headers_service, services=services,
                    headers_doctors=headers_doctors, doctors=doctors,
                    total_cost=total_cost)

        return render_template('services.html', **data)


@app.route('/services/new', methods=['GET', 'POST'])
def new_service():
    if request.method == 'GET':
        with create_session() as session:
            _, doctors = querys.get_list_doctors(session)
        return render_template('new_service.html', doctors=doctors)
    elif request.method == 'POST':
        data = request.form.to_dict()
        print(data)
        with create_session() as session:
            try:
                querys.add_service(session, data, data['d_id'])
            except Exception as e:
                error_message = e.args[0]
                return redirect(url_for('error_page', message=error_message))
            return redirect(url_for('get_list_services'))


@app.route('/services/delete/<int:id_service>', methods=['GET'])
def delete_service(id_service: int):
    with create_session() as session:
        querys.delete_services(session, id_service)
        return redirect(url_for('get_list_services'))


@app.route('/services/update/<int:id_service>', methods=['GET'])
def update_service(id_service: int):
    with create_session() as session:
        data = request.args.to_dict()
        price = data.get('price')
        if price:
            querys.update_services(session, id_service, price)
            return redirect(url_for('get_list_services'))


@app.route('/services/get_doctor/<int:office>', methods=['GET'])
def get_special_services(office: int):
    with create_session() as session:
        services = querys.get_service_special_doctor(session, office)
        return services


@app.route('/visits', methods=['GET'])
def get_all_visits():
    with create_session() as session:
        headers_schedule, contact_headers_schedule, schedule, contact_schedule = querys.get_schedule(session)
        headers_visits, visits = querys.get_all_visits(session)

        data = dict(user=user, headers_schedule=headers_schedule,
                    contact_headers_schedule=contact_headers_schedule,
                    schedule=schedule, contact_schedule=contact_schedule,
                    headers_visits=headers_visits, visits=visits)
    return render_template('visits.html', **data)


@app.route('/error')
def error_page():
    error_message = request.args.get('message', """Что-то пошло не так.
                                    Пожалуйста, попробуйте еще раз.""")
    return render_template('error.html', error_message=error_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
