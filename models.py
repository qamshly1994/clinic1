from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default="doctor")  # doctor / admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patients = db.relationship("Patient", backref="doctor", lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(50))
    notes = db.Column(db.Text)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sessions = db.relationship("Session", backref="patient", lazy=True)
    appointments = db.relationship("Appointment", backref="patient", lazy=True)
    invoices = db.relationship("Invoice", backref="patient", lazy=True)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    weight = db.Column(db.Float)
    belly_before = db.Column(db.Float)
    belly_after = db.Column(db.Float)
    waist_before = db.Column(db.Float)
    waist_after = db.Column(db.Float)
    hip = db.Column(db.Float)
    arms = db.Column(db.Float)
    thighs = db.Column(db.Float)
    notes = db.Column(db.Text)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="scheduled")  # scheduled / completed / canceled
    notes = db.Column(db.Text)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="paid")  # جميع الفواتير نقداً
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

