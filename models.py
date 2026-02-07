from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid

db = SQLAlchemy()

# ===== Doctor =====
class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    specialty = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patients = db.relationship("Patient", backref="doctor", lazy=True)


# ===== Patient =====
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))

    assessment = db.relationship("NutritionAssessment", backref="patient", uselist=False)
    sessions = db.relationship("Session", backref="patient", lazy=True)


# ===== Nutrition Assessment (الاستبيان) =====
class NutritionAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))

    medical_history = db.Column(db.Text)
    dietary_habits = db.Column(db.Text)
    activity_level = db.Column(db.String(100))
    goal = db.Column(db.Text)
    pregnancy = db.Column(db.String(50))


# ===== Sessions (الجلسات المتكررة) =====
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    date = db.Column(db.Date, default=datetime.utcnow)

    weight = db.Column(db.Float)

    waist_before = db.Column(db.Float)
    waist_after = db.Column(db.Float)

    belly_before = db.Column(db.Float)
    belly_after = db.Column(db.Float)

    hip = db.Column(db.Float)
    arms = db.Column(db.Float)
    thighs = db.Column(db.Float)
