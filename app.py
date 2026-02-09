import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
from models import db, Doctor, Patient, Session, Appointment, Invoice
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# ===== User Class =====
class DoctorUser(UserMixin):
    def __init__(self, doctor):
        self.id = doctor.id
        self.username = doctor.username
        self.role = doctor.role
        self.full_name = doctor.full_name

@login_manager.user_loader
def load_user(user_id):
    doctor = Doctor.query.get(int(user_id))
    if doctor:
        return DoctorUser(doctor)
    return None

# ===== Health Check =====
@app.route("/health")
def health():
    return "OK", 200

# ===== Login / Logout =====
@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        doctor = Doctor.query.filter_by(username=username).first()
        if doctor and bcrypt.check_password_hash(doctor.password_hash, password):
            login_user(DoctorUser(doctor))
            return redirect(url_for("dashboard"))
        else:
            flash("بيانات الدخول غير صحيحة")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ===== Dashboard =====
@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role=="admin":
        patients = Patient.query.order_by(Patient.created_at.desc()).all()
    else:
        patients = Patient.query.filter_by(doctor_id=current_user.id).order_by(Patient.created_at.desc()).all()
    return render_template("dashboard.html", doctor=current_user, patients=patients)

# ===== Add Patient =====
@app.route("/add_patient", methods=["GET","POST"])
@login_required
def add_patient():
    if request.method=="POST":
        name = request.form["name"]
        section = request.form["section"]
        notes = request.form.get("notes","")
        doctor_id = request.form.get("doctor_id") or current_user.id
        patient = Patient(name=name, section=section, notes=notes, doctor_id=doctor_id)
        db.session.add(patient)
        db.session.commit()
        flash("تم إضافة المريض بنجاح")
        return redirect(url_for("dashboard"))
    doctors = Doctor.query.all() if current_user.role=="admin" else [current_user]
    return render_template("add_patient.html", doctors=doctors)

# ===== Patient Detail =====
@app.route("/patient/<int:patient_id>", methods=["GET","POST"])
@login_required
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if current_user.role!="admin" and patient.doctor_id!=current_user.id:
        flash("غير مصرح بالوصول لهذا المريض")
        return redirect(url_for("dashboard"))
    if request.method=="POST":
        session = Session(
            patient_id=patient.id,
            date=datetime.strptime(request.form["date"], "%Y-%m-%d"),
            weight=float(request.form.get("weight",0)),
            belly_before=float(request.form.get("belly_before",0)),
            belly_after=float(request.form.get("belly_after",0)),
            waist_before=float(request.form.get("waist_before",0)),
            waist_after=float(request.form.get("waist_after",0)),
            hip=float(request.form.get("hip",0)),
            arms=float(request.form.get("arms",0)),
            thighs=float(request.form.get("thighs",0)),
            notes=request.form.get("notes","")
        )
        db.session.add(session)
        db.session.commit()
        flash("تم إضافة الجلسة بنجاح")
        return redirect(url_for("patient_detail", patient_id=patient.id))
    sessions = Session.query.filter_by(patient_id=patient.id).order_by(Session.date.desc()).all()
    return render_template("patient_detail.html", patient=patient, sessions=sessions)

# ===== Add Doctor (Admin only) =====
@app.route("/add_doctor", methods=["GET","POST"])
@login_required
def add_doctor():
    if current_user.role!="admin":
        flash("غير مصرح بالوصول لهذه الصفحة")
        return redirect(url_for("dashboard"))
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        full_name = request.form["full_name"]
        role = request.form.get("role","doctor")
        if Doctor.query.filter_by(username=username).first():
            flash("اسم المستخدم موجود مسبقاً")
            return redirect(url_for("add_doctor"))
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        new_doctor = Doctor(username=username, password_hash=password_hash, full_name=full_name, role=role)
        db.session.add(new_doctor)
        db.session.commit()
        flash("تم إضافة الدكتور بنجاح")
        return redirect(url_for("dashboard"))
    return render_template("add_doctor.html")

# ===== Initialize DB =====
def init_db():
    with app.app_context():
        db.create_all()
        if not Doctor.query.filter_by(username="admin").first():
            password = bcrypt.generate_password_hash("Admin@123").decode("utf-8")
            admin = Doctor(username="admin", password_hash=password, full_name="مدير العيادة", role="admin")
            db.session.add(admin)
            db.session.commit()
init_db()
