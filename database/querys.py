from datetime import time, datetime, date
from sqlalchemy import select, text, delete, update, insert
from sqlalchemy.orm import Session

from database.models import Patient, Doctor, Service, Appointment, DoctorService, AppointmentService


def get_total_cost(session: Session):
    res = session.execute(text("SELECT total_cost();"))
    total_cost = res.fetchone()[0]
    return total_cost


def get_patients(session: Session):
    headers = ("Полис", "ФИО", "Дата рождения", "Паспорт", "Телефон", "Почта",
               'Удаление пациента')

    stmt = """SELECT polis, fio_patient, bd_patient,
                passport, phone_patient, email_patient
                FROM patients"""
    res = session.execute(text(stmt)).all()
    res = [dict(polis=el[0], fio=el[1], bd=el[2], passport=el[3],
                phone=el[4], email=el[5]) for el in res]
    return headers, res


def delete_patients(session: Session, polis: str):

    session.execute(text(f"call delete_patient_proc('{polis}')"))
    session.commit()


def add_patients(session: Session, partient: dict):
    if session.get(Patient, partient.get('polis')):
        raise Exception('Пациент с таким полисом уже существует!')

    string = ', '.join([f"'{val}'" for val in partient.values()])

    session.execute(text(f"call insert_patient_proc({string})"))
    session.commit()


def get_patients_without_appointments(session: Session):
    headers = ("ФИО", "Полис")

    # Запрос к вашей созданной функции в базе данных
    stmt = """SELECT * FROM get_patients_without_appointments()"""
    res = session.execute(text(stmt)).all()

    # Преобразование результата в список словарей
    res = [dict(fio=el[0], polis=el[1]) for el in res]
    return headers, res


def get_appointments(session: Session):
    headers = ('ID записи', 'Полис', 'Пациент', 'Дата', 'Время', 'Врач', 
               'Кабинет', 'Услуга', 'Добавление услуги', 'Удаление записи')

    stmt = ''' SELECT
                a.id_appointment,
                a.polis,
                p.fio_patient,
                a.date_appointment,
                a.time_appointment,
                d.fio_doctor,
                a.office,
                COALESCE(s.name_service, 'Нет услуги') AS service_name
                FROM appointments AS a
                JOIN patients AS p ON p.polis = a.polis
                JOIN doctors AS d ON d.office = a.office
                LEFT JOIN appointment_service AS aps ON aps.id_appointment = a.id_appointment
                LEFT JOIN services AS s ON s.id_service = aps.id_service
                ORDER BY  a.date_appointment, a.time_appointment; '''

    res = session.execute(text(stmt)).all()
    return headers, [dict(id_appointment=el[0], polis=el[1],
                          patient=el[2], date=el[3],
                          time=el[4].strftime("%H:%M"), doctor=el[5],
                          office=el[6], service_name=el[7]) for el in res]


def day_of_week(mydate):
    days = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье"
    }
    day = mydate.weekday()
    return days[day]


def add_appointments(session: Session, p_id: str, d_id: int, day: str, my_time: str):
    day = datetime.strptime(day, '%Y-%m-%d')
    day_of_week_name = day_of_week(day)

    my_time = my_time.split(':')
    my_time = time(int(my_time[0]), int(my_time[1]))

    # Получение времени открытия и закрытия клиники
    result = session.execute(
        text('SELECT open_time, close_time FROM clinic WHERE work_days = :day_of_week'),
        {"day_of_week": day_of_week_name}
    ).fetchone()

    if result:
        open_time, close_time = result
    else:
        raise Exception("Данные о времени работы клиники не найдены.")

    if not (open_time <= my_time < close_time):
        raise Exception('Поликлиника закрыта в это время, попробуйте записаться в рабочее время :)')

    stmt = text("""SELECT polis FROM appointments
        WHERE polis = :p_id AND date_appointment = :day AND time_appointment = :time
    """)
    if session.execute(stmt, {"p_id": p_id, "day": day, "time": my_time}).fetchone():
        raise Exception('У пациента уже есть запись на эти дату и время')

    stmt = text("""
        SELECT office
        FROM appointments
        WHERE office = :d_id AND date_appointment = :day AND time_appointment = :time
    """)
    if session.execute(stmt, {"d_id": d_id, "day": day, "time": my_time}).fetchone():
        raise Exception('У доктора уже есть прием в это время!')

    number = session.execute(text('SELECT max(id_appointment) FROM appointments')).scalar()

    stmt = text("""
        INSERT INTO appointments (id_appointment, polis, date_appointment, time_appointment, office, id_clinic, id_editor)
        VALUES (:id, :p_id, :day, :time, :d_id, 1, 1)
    """)
    session.execute(stmt, {
        "id": number + 1 if number else 1,  # Если number = None, используем 1
        "p_id": p_id,
        "day": day,
        "time": my_time,
        "d_id": d_id
    })

    session.commit()


def delete_appointment(session: Session, id_appointment: int):
    stmt = text("""DELETE FROM appointments
                WHERE id_appointment = :id_appointment""")
    print(stmt)
    session.execute(stmt, {"id_appointment": id_appointment})
    session.commit()


def get_list_doctors(session: Session):
    headers = ('ФИО', 'Специальность', 'Кабинет', 'Удаление врача')

    stmt = select(Doctor.fio_doctor, Doctor.speciality, Doctor.office).order_by(Doctor.office)

    res = session.execute(stmt).all()
    return headers, [dict(fio=el[0], speciality=el[1],
                          office=el[2]) for el in res]


def add_doctor(session: Session, doctor: dict):
    if session.get(Doctor, doctor.get('office')):
        raise Exception('Этот кабинет уже занят другим врачом')

    stmt = insert(Doctor).values(fio_doctor=doctor.get('fio_doctor'),
                                speciality=doctor.get('speciality'),
                                office=doctor.get('office'))

    session.execute(stmt)
    session.commit()


def delete_doctor(session: Session, office: int):
    stmt = delete(Doctor).where(Doctor.office == office)

    session.execute(stmt)
    session.commit()


# def get_services(session: Session):
#     headers = ('ID', 'Название', 'Цена')

#     stmt = select(Service.id_service, Service.name_service, Service.price).order_by(Service.id_service)

#     res = session.execute(stmt).all()
#     return headers, [dict(id=el[0], name=el[1], price=el[2]) for el in res]

def get_services(session: Session):
    headers = ('ID', 'Название', 'Цена', 'Врач', 'Специальность врача')

    # Объединяем таблицы services, doctor_service и doctors, чтобы извлечь информацию о врачах для каждой услуги.
    stmt = (
        select(Service.id_service, Service.name_service, Service.price, Doctor.fio_doctor, Doctor.speciality)
        .join(DoctorService, Service.id_service == DoctorService.id_service)
        .join(Doctor, DoctorService.office == Doctor.office)
        .order_by(Service.id_service)
    )

    res = session.execute(stmt).all()
    return headers, [
        dict(id=el[0], name=el[1], price=el[2], doctor=el[3], speciality=el[4])
        for el in res
    ]


def get_service_special_doctor(session: Session, d_id: int):
    stmt = (
        select(Service.id_service, Service.name_service)
        .join(DoctorService, Service.id_service == DoctorService.id_service)
        .join(Doctor, DoctorService.office == Doctor.office)
        .where(Doctor.office == d_id)
    )

    res = session.execute(stmt).all()
    return [dict(id=el[0], name=el[1]) for el in res]


def delete_services(session: Session, id_service: int):
    session.execute(delete(DoctorService).where(DoctorService.id_service == id_service))
    session.execute(delete(Service).where(Service.id_service == id_service))
    session.commit()


def add_service(session: Session, service: dict, office: int):
    if session.get(Service, service.get('id_service')):
        raise Exception('Услуга с таким ID уже существует!')

    stmt = insert(Service).values(id_service=service.get('id_service'),
                                  name_service=service.get('name_service'),
                                #   d_id=office,
                                  price=service.get('price'))
    stmt2 = insert(DoctorService).values(id_service=service.get('id_service'),
                                         office=office)

    session.execute(stmt)
    session.execute(stmt2)
    session.commit()


def update_services(session: Session, id_service: int, price: float):

    session.execute(update(Service).where(Service.id_service == id_service).values(price=price))
    session.commit()


def get_all_visits(session: Session):
    headers = ('ФИО пациента', 'ФИО врача', 'Специальность врача',
               'Количество посещений')

    stmt = '''SELECT v.fio_patient, v.fio_doctor, v.speciality,
            v.visit_count FROM all_visits AS v ORDER BY v.fio_patient'''

    res = session.execute(text(stmt)).all()
    return headers, [dict(fio_patient=el[0], fio_doctor=el[1],
                          speciality_doctor=el[2], visit_count=el[3]) for el in res]


def insert_appointment_service(session: Session, id_appointment: int, id_service: int):
    stmt = insert(AppointmentService).values(id_appointment=id_appointment, id_service= id_service)
    session.execute(stmt)
    session.commit()

def get_schedule(session: Session):
    data_headers = ('Дни работы', 'Время открытия', 'Время закрытия')
    contact_data_headers = ('Адрес', 'Телефон', 'Почта')

    stmt = 'SELECT * FROM clinic'

    data = []
    contact_data = None
    res = session.execute(text(stmt)).all()
    for el in res:
        data.append(dict(work_days=el[2], open_time=el[3].strftime("%H:%M"),
                         close_time=el[4].strftime("%H:%M")))
        if not contact_data:
            contact_data = [el[1], el[5], el[6]]
    return data_headers, contact_data_headers, data, contact_data


def get_user_from_db(session: Session, polis: str):

    user = session.get(Patient, polis)
    return user
