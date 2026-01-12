from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, default="student")

    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    gender = Column(String, nullable=True)

    faculty = Column(String, nullable=True)
    course = Column(String, nullable=True)
    level = Column(Integer, nullable=True)

    matric_no = Column(String, unique=True, index=True)
    password_hash = Column(String)

    photo = Column(String, nullable=True)
    course_form_pdf = Column(String, nullable=True)


    # ================= SCHOOL FEES =================
    fees_total = Column(Integer, default=150000)
    fees_paid = Column(Integer, default=0)


    # ================= ACCESS CONTROL =================
    access_percentage = Column(Integer, default=0)
    accessible_weeks = Column(Integer, default=0)

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))

    course = Column(String)
    ca_score = Column(Integer)
    exam_score = Column(Integer)
    total = Column(Integer)
    grade = Column(String)
    remark = Column(String)

    # ✅ NEW (CRITICAL)
    semester = Column(String)
    level = Column(Integer)
    session = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", backref="results")



class AppConfig(Base):
    __tablename__ = "app_config"

    id = Column(Integer, primary_key=True)
    active_semester = Column(String, default="first")



class SemesterLog(Base):
    __tablename__ = "semester_logs"

    id = Column(Integer, primary_key=True)
    old_semester = Column(String)
    new_semester = Column(String)
    changed_by = Column(String)
    changed_at = Column(DateTime, default=datetime.utcnow)

    from sqlalchemy import Column, Integer, String, Text

class CourseContent(Base):
    __tablename__ = "course_content"

    id = Column(Integer, primary_key=True)
    course_code = Column(String, index=True)
    faculty = Column(String, index=True)   # ✅ NEW
    level = Column(Integer, index=True)    # ✅ NEW
    semester = Column(String, index=True)  # ✅ NEW

    week = Column(Integer)
    title = Column(String)
    content = Column(Text)
    pdf = Column(String, nullable=True)
    audio = Column(String, nullable=True)




class CourseFormPayment(Base):
    __tablename__ = "course_form_payments"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    semester = Column(String)
    amount = Column(Integer, default=5000)
    paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class StudentAccess(Base):
    __tablename__ = "student_access"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    session = Column(String)
    access_percentage = Column(Integer, default=0)
    accessible_weeks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClassMessage(Base):
    __tablename__ = "class_messages"

    id = Column(Integer, primary_key=True)
    course_code = Column(String, index=True)
    week = Column(Integer)
    sender_role = Column(String)  # "admin" or "student"
    sender_name = Column(String)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_code = Column(String)
    week = Column(Integer)
    semester = Column(String)
    session = Column(String)
    attended_at = Column(DateTime, default=datetime.utcnow)

class ClassReplay(Base):
    __tablename__ = "class_replay"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer)
    course_code = Column(String)
    week = Column(Integer)
    seconds_spent = Column(Integer, default=0)
    replay_count = Column(Integer, default=0)
    last_seen = Column(DateTime, default=datetime.utcnow)

class PaymentHistory(Base):
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    method = Column(String)   # "paystack" or "manual"
    reference = Column(String, nullable=True)
    receipt = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", backref="payments")

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text

class AdmissionApplication(Base):
    __tablename__ = "admission_applications"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    gender = Column(String(20))
    dob = Column(String(50))
    admission_type = Column(String(50))
    faculty = Column(String(255))
    course = Column(String(255))

    nin_file = Column(String(255))
    birth_cert_file = Column(String(255))
    olevel_file = Column(String(255))
    passport_file = Column(String(255))
    transcript_file = Column(String(255), nullable=True)

    payment_ref = Column(String(255))
    payment_amount = Column(Integer, default=15000)

    tracking_code = Column(String(100), unique=True, index=True)

    status = Column(Enum(
        "PENDING_PAYMENT",
        "PAID",
        "SCREENING",
        "ACCEPTED",
        "REJECTED",
        "ADMITTED",
        name="admission_status"
    ), default="PENDING_PAYMENT")

    # ADD THESE 2 ↓↓↓
    offer_letter_url = Column(String(255), nullable=True)
    offer_letter_sent_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

class StudentLevel(Base):
    __tablename__ = "student_levels"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    old_level = Column(Integer)
    new_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
