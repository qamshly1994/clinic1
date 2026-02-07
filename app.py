import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
from models import db, Doctor, Patient, Session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
db_url = os.environ.get("DATABASE_URL", "sqlite:///clinic.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# ===== User Class =====
class DoctorUser(UserMixin):
    def __init__(self, doctor):
        self.id = doctor.id
        self.username = doctor.username

@login_manager.user_loader
def load_user(user_id):
    doctor = Doctor.query.get(int(user_id))
    if doctor:
        return DoctorUser(doctor)
    return None

# ===== Routes =====

@app.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        doctor = Doctor.query.filter_by(username=username).first()
        if doctor and bcrypt.check_password_hash(doctor.password_hash, password):
            login_user(DoctorUser(doctor), remember=True)
            return redirect(url_for("dashboard"))
        else:
            flash("بيانات الدخول غير صحيحة")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    doctor = Doctor.query.get(current_user.id)
    patients = Patient.query.filter_by(doctor_id=doctor.id).order_by(Patient.created_at.desc()).all()
    return render_template("dashboard.html", doctor=doctor, patients=patients)

@app.route("/add_patient", methods=["GET", "POST"])
@login_required
def add_patient():
    if request.method == "POST":
        name = request.form["name"]
        section = request.form["section"]
        notes = request.form.get("notes", "")
        doctor = Doctor.query.get(current_user.id)
        patient = Patient(name=name, section=section, notes=notes, doctor=doctor)
        db.session.add(patient)
        db.session.commit()
        flash("تم إضافة المريض بنجاح")
        return redirect(url_for("dashboard"))
    return render_template("add_patient.html")

@app.route("/patient/<int:patient_id>", methods=["GET", "POST"])
@login_required
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.doctor_id != current_user.id:
        flash("غير مصرح بالوصول لهذا المريض")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        date = request.form.get("date")
        weight = float(request.form.get("weight", 0))
        belly_before = float(request.form.get("belly_before", 0))
        belly_after = float(request.form.get("belly_after", 0))
        waist_before = float(request.form.get("waist_before", 0))
        waist_after = float(request.form.get("waist_after", 0))
        hip = float(request.form.get("hip", 0))
        arms = float(request.form.get("arms", 0))
        thighs = float(request.form.get("thighs", 0))
        notes = request.form.get("notes", "")

        session = Session(
            patient=patient,
            date=datetime.strptime(date, "%Y-%m-%d"),
            weight=weight,
            belly_before=belly_before,
            belly_after=belly_after,
            waist_before=waist_before,
            waist_after=waist_after,
            hip=hip,
            arms=arms,
            thighs=thighs,
            notes=notes
        )
        db.session.add(session)
        db.session.commit()
        flash("تم إضافة الجلسة بنجاح")
        return redirect(url_for("patient_detail", patient_id=patient.id))

    sessions = Session.query.filter_by(patient_id=patient.id).order_by(Session.date.desc()).all()
    return render_template("patient_detail.html", patient=patient, sessions=sessions)

@app.route("/add_doctor", methods=["GET", "POST"])
@login_required
def add_doctor():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        full_name = request.form["full_name"]

        if Doctor.query.filter_by(username=username).first():
            flash("اسم المستخدم موجود مسبقاً")
            return redirect(url_for("add_doctor"))

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        new_doctor = Doctor(username=username, password_hash=password_hash, full_name=full_name)
        db.session.add(new_doctor)
        db.session.commit()

        flash("تم إضافة الدكتور بنجاح")
        return redirect(url_for("dashboard"))

    return render_template("add_doctor.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ===== Initialize DB =====
with app.app_context():
    db.create_all()
    if not Doctor.query.filter_by(username="master").first():
        password = bcrypt.generate_password_hash("Master@123").decode("utf-8")
        admin = Doctor(username="master", password_hash=password, full_name="مدير العيادة")
        db.session.add(admin)
        db.session.commit()

# ===== Run server =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
