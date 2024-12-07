
from sqlalchemy import String, Integer, Date, Time, ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
    pass


class Patient(Base):
    __tablename__ = 'patients'
    polis: Mapped[str] = mapped_column(String(50), primary_key=True)
    fio_patient: Mapped[str] = mapped_column(String(255), nullable=False)
    bd_patient: Mapped[Date] = mapped_column(Date, nullable=False)
    passport: Mapped[str] = mapped_column(String(50))
    phone_patient: Mapped[str] = mapped_column(String(20))
    email_patient: Mapped[str] = mapped_column(String(100))
    password: Mapped[str]


class Clinic(Base):
    __tablename__ = 'clinic'
    id_clinic: Mapped[int] = mapped_column(Integer, primary_key=True)
    adres: Mapped[str] = mapped_column(String(255))
    work_days: Mapped[str] = mapped_column(String(100))
    open_time: Mapped[Time] = mapped_column(Time)
    close_time: Mapped[Time] = mapped_column(Time)
    phone_clinic: Mapped[str] = mapped_column(String(20))
    email_clinic: Mapped[str] = mapped_column(String(100))


class Editor(Base):
    __tablename__ = 'editor'
    id_editor: Mapped[int] = mapped_column(Integer, primary_key=True)
    fio_editor: Mapped[str] = mapped_column(String(255))
    post_editor: Mapped[str] = mapped_column(String(100))
    phone_editor: Mapped[str] = mapped_column(String(20))


class Doctor(Base):
    __tablename__ = 'doctors'
    office: Mapped[int] = mapped_column(Integer, primary_key=True)
    fio_doctor: Mapped[str] = mapped_column(String(255), nullable=False)
    speciality: Mapped[str] = mapped_column(String(100))


class Service(Base):
    __tablename__ = 'services'
    id_service: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_service: Mapped[str] = mapped_column(String(255))
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2))


class DoctorService(Base):
    __tablename__ = 'doctor_service'
    office: Mapped[int] = mapped_column(ForeignKey('doctors.office', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)
    id_service: Mapped[int] = mapped_column(ForeignKey('services.id_service', ondelete='SET NULL', onupdate='CASCADE'), primary_key=True)


class Appointment(Base):
    __tablename__ = 'appointments'
    id_appointment: Mapped[int] = mapped_column(Integer, primary_key=True)
    polis: Mapped[str] = mapped_column(ForeignKey('patients.polis', ondelete='CASCADE', onupdate='RESTRICT'))
    date_appointment: Mapped[Date] = mapped_column(Date)
    time_appointment: Mapped[Time] = mapped_column(Time)
    office: Mapped[int] = mapped_column(ForeignKey('doctors.office', ondelete='CASCADE', onupdate='CASCADE'))
    id_clinic: Mapped[int] = mapped_column(ForeignKey('clinic.id_clinic', ondelete='CASCADE', onupdate='CASCADE'))
    id_editor: Mapped[int] = mapped_column(ForeignKey('editor.id_editor', ondelete='SET NULL', onupdate='RESTRICT'))


class AppointmentService(Base):
    __tablename__ = 'appointment_service'
    id_appointment: Mapped[int] = mapped_column(ForeignKey('appointments.id_appointment', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    id_service: Mapped[int] = mapped_column(ForeignKey('services.id_service', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
