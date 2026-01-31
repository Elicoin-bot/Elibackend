from fastapi import (
    FastAPI, HTTPException, Depends,
    Header, UploadFile, File, Form
)
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from models import Result
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import func
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User
from pydantic import BaseModel
from models import AppConfig, SemesterLog
from models import CourseContent, ClassMessage, ClassReplay, AdmissionApplication
from models import CourseFormPayment, StudentLevel, Attendance, PaymentHistory 
from dotenv import load_dotenv

load_dotenv()


import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import os, uuid, shutil

import requests






FLW_SECRET_KEY = os.getenv("FLW_SECRET_KEY")
if not FLW_SECRET_KEY:
    print("WARNING: FLW_SECRET_KEY missing!")


PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_INIT_URL = "https://api.paystack.co/transaction/initialize"
PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/"

FACULTY_FEES = {
    "FACULTY OF PURE AND APPLIED SCIENCE": 250000,
    "FACULTY OF ENGINEERING": 250000,
    "FACULTY OF ART AND HUMANITIES": 200000,
    "FACULTY OF MANAGEMENT SCIENCE": 180000,
    "FACULTY OF SOCIAL SCIENCE": 180000
}

TOTAL_SEMESTER_WEEKS = 12

FACULTY_COURSES = {
    "FACULTY OF PURE AND APPLIED SCIENCE": [
        "Nursing Science",
        "Computer Science"
    ],
    "FACULTY OF MANAGEMENT SCIENCE": [
        "Accounting",
        "Banking and Finance",
        "Marketing",
        "Business Administration and Management",
        "Human Resources Management",
        "Transport and Logistics Management"
    ],
    "FACULTY OF SOCIAL SCIENCE": [
        "Economics",
        "Political Science",
        "Public Administration"
    ],
    "FACULTY OF ART AND HUMANITIES": [
        "Mass Communication",
        "International Relations and Diplomacy"
    ],
    "FACULTY OF ENGINEERING": [
        "Computer Engineering"
    ]
}

COURSES_BY_FACULTY = {
    "FACULTY OF PURE AND APPLIED SCIENCE": {
        "Nursing Science": 12,
        "Computer Science": 12
    },
    "FACULTY OF MANAGEMENT SCIENCE": {
        "Accounting": 12,
        "Banking and Finance": 12,
        "Marketing": 12,
        "Business Administration and Management": 12,
        "Human Resources Management": 12,
        "Transport and Logistics Management": 12
    },
    "FACULTY OF SOCIAL SCIENCE": {
        "Economics": 12,
        "Political Science": 12,
        "Public Administration": 12
    },
    "FACULTY OF ART AND HUMANITIES": {
        "Mass Communication": 12,
        "International Relations and Diplomacy": 12
    },
    "FACULTY OF ENGINEERING": {
        "Computer Engineering": 12
    }
}

COURSE_REGISTRY = {

# ======================================================
# FACULTY OF PURE & APPLIED SCIENCE
# ======================================================



"Computer Science": {

    100: {
        "first": [
            {"code": "GNS101", "title": "Use of English", "unit": 2},
            {"code": "GNS103", "title": "Introduction to Philosophy", "unit": 2},
            {"code": "GNS105", "title": "Basic Study Skills", "unit": 2},
            {"code": "ECN101", "title": "Introduction to Economics I", "unit": 2},
            {"code": "PHS101", "title": "General Physics I", "unit": 3},
            {"code": "MTH103", "title": "Basic Algebra", "unit": 3},
            {"code": "CSC101", "title": "Introduction to Computer Science", "unit": 3},
            {"code": "CHM101", "title": "General Chemistry", "unit": 3},
            {"code": "STS107", "title": "Introduction to Statistics", "unit": 2},
        ],
        "second": [
            {"code": "GNS102", "title": "Logic and Reasoning", "unit": 2},
            {"code": "GNS104", "title": "Politics and Government", "unit": 2},
            {"code": "GNS106", "title": "Literature in English", "unit": 2},
            {"code": "MTH102", "title": "Introduction to Calculus", "unit": 3},
            {"code": "PHS102", "title": "General Physics II", "unit": 2},
            {"code": "CSC102", "title": "Basic Programming", "unit": 3},
            {"code": "CSC104", "title": "Computer System Modelling", "unit": 3},
            {"code": "CSC106", "title": "Vector Geometry", "unit": 2},
            {"code": "CSC108", "title": "Business Programming (COBOL)", "unit": 3},
            {"code": "CHM102", "title": "General Chemistry II", "unit": 2},
            {"code": "LIS102", "title": "Introduction to Libraries", "unit": 3},
        ]
    },

    200: {
        "first": [
            {"code": "CSC/MIT205", "title": "Management Information System", "unit": 3},
            {"code": "CSC/MIT211", "title": "Elementary Data Processing & Data Structure", "unit": 2},
            {"code": "CSC203", "title": "Computer Application", "unit": 2},
            {"code": "MIT209", "title": "Human–Computer Interaction", "unit": 2},
            {"code": "MTH203", "title": "Mathematical Methods for Social Science", "unit": 3},
        ],
        "second": [
            {"code": "MTH202", "title": "Numerical Analysis", "unit": 3},
            {"code": "MIT204", "title": "Database Development & Management", "unit": 3},
            {"code": "MTH206", "title": "Mathematical Methods II", "unit": 3},
            {"code": "MIT210", "title": "Information Storage & Retrieval", "unit": 2},
            {"code": "CSC202", "title": "Differential Equation", "unit": 3},
            {"code": "CSC204", "title": "Information Products & Services", "unit": 3},
            {"code": "CSC206", "title": "Human Computer Interaction", "unit": 3},
            {"code": "CSC208", "title": "Computer Repairs & Maintenance", "unit": 2},
        ]
    },

    300: {
        "first": [
            {"code": "CSC311", "title": "Seminar / Independent Study", "unit": 2},
            {"code": "CSC303", "title": "Symbolic Programming in FORTRAN", "unit": 2},
            {"code": "CSC305", "title": "Computer Architecture", "unit": 3},
            {"code": "CSC307", "title": "Compiler Construction", "unit": 3},
            {"code": "MIT209", "title": "Human–Computer Interaction", "unit": 2},
            {"code": "CSC315", "title": "Data Structure and Algorithm", "unit": 3},
            {"code": "CSC203", "title": "Computer Application", "unit": 2},
        ],
        "second": [
            {"code": "CSC300", "title": "Research Project", "unit": 6},
            {"code": "CSC302", "title": "Introduction to Internet Computing", "unit": 3},
            {"code": "CSC304", "title": "Artificial Intelligence", "unit": 3},
            {"code": "CSC306", "title": "Cryptography & IT Security", "unit": 3},
            {"code": "CSC308", "title": "System Analysis & Design", "unit": 3},
            {"code": "CSC310", "title": "Mobile & Cloud Computing", "unit": 3},
            {"code": "CSC312", "title": "Computer Installation Management", "unit": 3},
            {"code": "CSC314", "title": "Advanced Software Engineering", "unit": 3},
        ]
    }
},

# ======================================================
# FACULTY OF MANAGEMENT SCIENCE
# (Accounting, Banking & Finance, Business Admin, HRM, Economics)
# ======================================================

"Accounting, Banking & Finance, Business Administration And Management, HRM, Economics": {

    100: {
        "first": [
            {"code": "GNS101", "title": "Use of English", "unit": 2},
            {"code": "GNS103", "title": "Introduction to Philosophy", "unit": 2},
            {"code": "GNS105", "title": "Basic Study Skills", "unit": 2},
            {"code": "ECN101", "title": "Introduction to Economics I", "unit": 2},
            {"code": "BUS104", "title": "Principles of Management", "unit": 3},
            {"code": "CSC101", "title": "Introduction to Computer Science", "unit": 3},
            {"code": "BUS103", "title": "Introduction to Marketing", "unit": 3},
            {"code": "STS107", "title": "Introduction to Statistics", "unit": 2},
        ],
        "second": [
            {"code": "GNS102", "title": "Logic and Reasoning", "unit": 2},
            {"code": "GNS104", "title": "Politics and Government", "unit": 2},
            {"code": "GNS106", "title": "Literature in English", "unit": 2},
            {"code": "MTH104", "title": "Business Mathematics", "unit": 2},
            {"code": "BUS102", "title": "Introduction to Business Finance", "unit": 3},
            {"code": "ECO102", "title": "Introduction to Economics II", "unit": 3},
            {"code": "ACC102", "title": "Introduction to Accounting", "unit": 2},
            {"code": "BUS104", "title": "Principles of Management", "unit": 3},
            {"code": "MKT104", "title": "Management and Society", "unit": 3},
            {"code": "LIS102", "title": "Introduction to Libraries", "unit": 3},
        ]
    }
    
},

"Accounting": {
    200: {
        "first": [
            {"code": "ECN201", "title": "Microeconomics", "unit": 3},
            {"code": "BUS207", "title": "Management Theory and Principle", "unit": 3},
            {"code": "CSC/BUS205", "title": "Management Information System", "unit": 3},
            {"code": "ECN213", "title": "History and Structure of Nigerian Economy", "unit": 3},
            {"code": "CSC/BUS203", "title": "Computer Application for Business", "unit": 3},
            {"code": "MKT201", "title": "Principles of Marketing", "unit": 3},
            {"code": "ACC203", "title": "Introduction to Cost Accounting", "unit": 2},
            {"code": "ACC201", "title": "Financial Accounting I", "unit": 3},
        ],
        "second": [
        {"code": "BUS202", "title": "Organizational Behaviour", "unit": 3},
        {"code": "MIT210", "title": "Information Products & Services", "unit": 3},
        {"code": "ACC202", "title": "Financial Accounting II", "unit": 3},
        {"code": "ACC204", "title": "Cost Accounting II", "unit": 3},
        {"code": "HRM206", "title": "Human Resource Planning", "unit": 3},
        {"code": "ECN202", "title": "Macroeconomics", "unit": 3},
        {"code": "HRM202", "title": "Labour & Human Resource Economics", "unit": 2},
        {"code": "BUS208", "title": "Labour Law & Trade Unionism", "unit": 2},
        {"code": "ECN206", "title": "Econometrics I", "unit": 3},
    ]
    },
        300: {
        "first": [
            {"code": "ACC305", "title": "Taxation I", "unit": 3},
            {"code": "BUS303", "title": "Environment of International Business", "unit": 2},
            {"code": "ACC302", "title": "Advanced Financial Accounting I", "unit": 3},
            {"code": "BUS307", "title": "Small Scale Business Management", "unit": 2},
            {"code": "ACC309", "title": "Research Methodology", "unit": 2},
            {"code": "ACC301", "title": "Financial Management I", "unit": 3},
            {"code": "ACC303", "title": "Management Accounting I", "unit": 3},
            {"code": "ACC313", "title": "Auditing and Investigation I", "unit": 3},
            {"code": "ACC311", "title": "Seminar / Independent Study", "unit": 3},
        ],
        "second": [
        {"code": "ACC302", "title": "Financial Management II", "unit": 3},
        {"code": "BUS300", "title": "Project Research", "unit": 6},
        {"code": "BUS302", "title": "Operations Research", "unit": 3},
        {"code": "BUS304", "title": "Quantitative Techniques", "unit": 3},
        {"code": "ACC304", "title": "Management Accounting II", "unit": 3},
        {"code": "BUS306", "title": "Oil & Gas Tax Accounting", "unit": 2},
        {"code": "BUS310", "title": "Business Portfolio Management", "unit": 3},
        {"code": "MKT302", "title": "Integrated Marketing Communication", "unit": 2},
    ]
    }
},

"Economics": {
    200: {
        "first": [
            {"code": "ECN201", "title": "Microeconomics", "unit": 3},
            {"code": "BUS207", "title": "Management Theory and Principle", "unit": 3},
            {"code": "CSC/BUS205", "title": "Management Information System", "unit": 3},
            {"code": "ECN213", "title": "History and Structure of Nigerian Economy", "unit": 3},
            {"code": "CSC/BUS203", "title": "Computer Application for Business", "unit": 3},
            {"code": "MKT201", "title": "Principles of Marketing", "unit": 3},
            {"code": "ACC203", "title": "Introduction to Cost Accounting", "unit": 2},
            {"code": "MTH203", "title": "Mathematical Methods for Social Science", "unit": 3},
        ],

    
    "second": [
        {"code": "BUS202", "title": "Organizational Behaviour", "unit": 3},
        {"code": "MIT210", "title": "Information Products & Services", "unit": 3},
        {"code": "ACC202", "title": "Financial Accounting II", "unit": 3},
        {"code": "ACC204", "title": "Cost Accounting II", "unit": 3},
        {"code": "HRM206", "title": "Human Resource Planning", "unit": 3},
        {"code": "ECN202", "title": "Macroeconomics", "unit": 3},
        {"code": "HRM202", "title": "Labour & Human Resource Economics", "unit": 2},
        {"code": "BUS208", "title": "Labour Law & Trade Unionism", "unit": 2},
        {"code": "ECN206", "title": "Econometrics I", "unit": 3},
    ]


    },

    300: {
        "first": [
            {"code": "ECN301", "title": "Advanced Microeconomics Theory", "unit": 3},
            {"code": "ECN305", "title": "History of Economic Thought", "unit": 3},
            {"code": "BUS307", "title": "Small Scale Business Management", "unit": 2},
            {"code": "ECN309", "title": "Research Methodology", "unit": 2},
            {"code": "ECN307", "title": "Managerial Economics", "unit": 3},
            {"code": "ECN311", "title": "Seminar / Independent Study", "unit": 3},
            {"code": "ECN313", "title": "Development Problems in the Third World", "unit": 2},
            {"code": "ECN315", "title": "Energy and Petroleum Economics", "unit": 2},
        ],

        "second": [
            {"code": "ECN302", "title": "Advanced Macroeconomics Theory", "unit": 3},
            {"code": "BUS300", "title": "Project Research", "unit": 6},
            {"code": "BUS302", "title": "Operations Research", "unit": 3},
            {"code": "BUS304", "title": "Quantitative Techniques", "unit": 3},
            {"code": "ECN304", "title": "Managerial Economics", "unit": 3},
            {"code": "BUS306", "title": "Oil & Gas Tax Accounting", "unit": 2},
            {"code": "BUS310", "title": "Business Portfolio Management", "unit": 3},
            {"code": "MKT302", "title": "Integrated Marketing Communication", "unit": 2},
        ]
    }
},
"Human Resources Management": {
    200: {
        "first": [
            {"code": "ECN201", "title": "Microeconomics", "unit": 3},
            {"code": "BUS207", "title": "Management Theory and Principle", "unit": 3},
            {"code": "CSC/BUS205", "title": "Management Information System", "unit": 3},
            {"code": "HRM203", "title": "Introduction to Human Resources", "unit": 3},
            {"code": "CSC/BUS203", "title": "Computer Application for Business", "unit": 3},
            {"code": "MKT201", "title": "Principles of Marketing", "unit": 3},
            {"code": "ACC203", "title": "Introduction to Cost Accounting", "unit": 2},
            {"code": "MTH203", "title": "Mathematical Methods for Social Science", "unit": 3},
        ],

    
    "second": [
        {"code": "BUS202", "title": "Organizational Behaviour", "unit": 3},
        {"code": "MIT210", "title": "Information Products & Services", "unit": 3},
        {"code": "ACC202", "title": "Financial Accounting II", "unit": 3},
        {"code": "ACC204", "title": "Cost Accounting II", "unit": 3},
        {"code": "HRM206", "title": "Human Resource Planning", "unit": 3},
        {"code": "ECN202", "title": "Macroeconomics", "unit": 3},
        {"code": "HRM202", "title": "Labour & Human Resource Economics", "unit": 2},
        {"code": "BUS208", "title": "Labour Law & Trade Unionism", "unit": 2},
        {"code": "ECN206", "title": "Econometrics I", "unit": 3},
    ]
    },

    300: {
        "first": [
            {"code": "HRM301", "title": "Business Policy and Strategy", "unit": 3},
            {"code": "BUS303", "title": "International Business", "unit": 2},
            {"code": "HRM305", "title": "Human Resource Management", "unit": 3},
            {"code": "BUS307", "title": "Small Scale Business Management", "unit": 2},
            {"code": "BUS309", "title": "Research Methodology", "unit": 2},
            {"code": "ACC301", "title": "Financial Management I", "unit": 3},
            {"code": "ACC303", "title": "Management Accounting I", "unit": 3},
            {"code": "ECO301", "title": "Managerial Economics", "unit": 3},
            {"code": "BUS311", "title": "Seminar / Independent Study", "unit": 3},
        ],

        "second": [
            {"code": "ECN302", "title": "Advanced Macroeconomics Theory", "unit": 3},
            {"code": "BUS300", "title": "Project Research", "unit": 6},
            {"code": "BUS302", "title": "Operations Research", "unit": 3},
            {"code": "BUS304", "title": "Quantitative Techniques", "unit": 3},
            {"code": "ECN304", "title": "Managerial Economics", "unit": 3},
            {"code": "HRM306", "title": "Strategic Human Resource Management", "unit": 2},
            {"code": "BUS310", "title": "Business Portfolio Management", "unit": 3},
            {"code": "MKT302", "title": "Integrated Marketing Communication", "unit": 2},
        ]
    }
},
"Business Administration And Management": {

    200: {
        "first": [
            {"code": "BUS201", "title": "Principles of Management II", "unit": 3},
            {"code": "BUS203", "title": "Business Communication", "unit": 2},
            {"code": "BUS205", "title": "Organizational Behaviour", "unit": 3},
            {"code": "BUS207", "title": "Management Theory & Principles", "unit": 3},
            {"code": "BUS209", "title": "Business Statistics", "unit": 3},
            {"code": "BUS211", "title": "Introduction to Entrepreneurship", "unit": 2},
            {"code": "CSC/BUS205", "title": "Management Information System", "unit": 2},
            {"code": "ECN201", "title": "Microeconomics", "unit": 3},
        ],

        "second": [
        {"code": "BUS202", "title": "Organizational Behaviour", "unit": 3},
        {"code": "MIT210", "title": "Information Products & Services", "unit": 3},
        {"code": "ACC202", "title": "Financial Accounting II", "unit": 3},
        {"code": "ACC204", "title": "Cost Accounting II", "unit": 3},
        {"code": "HRM206", "title": "Human Resource Planning", "unit": 3},
        {"code": "ECN202", "title": "Macroeconomics", "unit": 3},
        {"code": "HRM202", "title": "Labour & Human Resource Economics", "unit": 2},
        {"code": "BUS208", "title": "Labour Law & Trade Unionism", "unit": 2},
        {"code": "ECN206", "title": "Econometrics I", "unit": 3},
    ]
    },

    300: {
        "first": [
            {"code": "BUS301", "title": "Business Policy & Strategy", "unit": 3},
            {"code": "BUS303", "title": "International Business Environment", "unit": 2},
            {"code": "BUS305", "title": "Human Resource Management", "unit": 3},
            {"code": "BUS307", "title": "Small-Scale Business Management", "unit": 2},
            {"code": "BUS309", "title": "Research Methodology", "unit": 2},
            {"code": "BUS311", "title": "Operations Management", "unit": 3},
            {"code": "BUS313", "title": "Entrepreneurship Development", "unit": 2},
            {"code": "BUS315", "title": "Seminar / Independent Study", "unit": 3},
        ],

        "second": [
            {"code": "ACC302", "title": "Financial Management II", "unit": 3},
            {"code": "BUS300", "title": "Project Research", "unit": 6},
            {"code": "BUS302", "title": "Operations Research", "unit": 3},
            {"code": "BUS304", "title": "Quantitative Techniques", "unit": 3},
            {"code": "ECN304", "title": "Managerial Economics", "unit": 3},
            {"code": "BUS306", "title": "Oil & Gas Tax Accounting", "unit": 2},
            {"code": "BUS310", "title": "Business Portfolio Management", "unit": 3},
            {"code": "MKT302", "title": "Integrated Marketing Communication", "unit": 2},
        ]
    }
},

# ======================================================
# FACULTY OF ART & HUMANITIES
# ======================================================

"Mass Communication": {

    100: {
        "first": [
            {"code": "GNS101", "title": "Use of English", "unit": 2},
            {"code": "GNS103", "title": "Introduction to Philosophy", "unit": 2},
            {"code": "GNS105", "title": "Basic Study Skills", "unit": 2},
            {"code": "ECN101", "title": "Introduction to Economics I", "unit": 2},
            {"code": "MCM101", "title": "Introduction to Mass Communication", "unit": 3},
            {"code": "MCM103", "title": "History of Mass Media", "unit": 3},
            {"code": "MCM107", "title": "Writing for Mass Media I", "unit": 3},
            {"code": "CSC101", "title": "Introduction to Computer", "unit": 3},
        ],

        "second": [
            {"code": "GNS102", "title": "Logic and Reasoning", "unit": 2},
            {"code": "GNS104", "title": "Politics and Government", "unit": 2},
            {"code": "GNS106", "title": "Literature in English", "unit": 2},
            {"code": "MCM102", "title": "Newspaper Reporting", "unit": 3},
            {"code": "MCM104", "title": "Introduction to Phonetics & Phonology II", "unit": 2},
            {"code": "MCM106", "title": "Advert Copy & Writing", "unit": 3},
            {"code": "MCM108", "title": "African Communication", "unit": 3},
            {"code": "SOC102", "title": "Introduction to Sociology", "unit": 2},
            {"code": "MCM110", "title": "Communication and Society", "unit": 3},
            {"code": "LIS102", "title": "Introduction to Libraries", "unit": 3},
        ]
    },

    200: {
        "first": [
            {"code": "MCM215", "title": "Theories of Mass Communication", "unit": 2},
            {"code": "MCM201", "title": "Foundation of Broadcasting", "unit": 2},
            {"code": "MCM203", "title": "Feature & Editing Writing", "unit": 2},
            {"code": "MCM205", "title": "Basics of Media Production", "unit": 3},
            {"code": "MCM217", "title": "Advertising in Mass Communication", "unit": 3},
            {"code": "MCM211", "title": "Investigative Reporting", "unit": 3},
            {"code": "MCM207", "title": "Features of Magazine Production", "unit": 2},
        ],

        "second": [
            {"code": "MCM204", "title": "Broadcast Journalism", "unit": 2},
            {"code": "MCM208", "title": "Introduction to Public Relations", "unit": 2},
            {"code": "MCM202", "title": "Book Publishing", "unit": 2},
            {"code": "MCM206", "title": "Publication Layout & Design", "unit": 3},
            {"code": "MCM210", "title": "Data Analysis in Communication Research", "unit": 3},
            {"code": "MCM212", "title": "Photo Editing", "unit": 3},
            {"code": "MCM214", "title": "Internship", "unit": 3},
            {"code": "MCM216", "title": "African Communication II", "unit": 3},
            {"code": "MIT210", "title": "Information Storage & Retrieval", "unit": 2},
        ]
    },
    
    300: {
        "first": [
            {"code": "MCM301", "title": "Advanced Reporting Techniques", "unit": 3},
            {"code": "MCM303", "title": "Broadcast Media Production", "unit": 3},
            {"code": "MCM305", "title": "Media Law and Ethics", "unit": 2},
            {"code": "MCM307", "title": "Development Communication", "unit": 3},
            {"code": "MCM309", "title": "Public Relations Practice", "unit": 3},
            {"code": "MCM311", "title": "Communication Research Methods", "unit": 2},
        ],
        
        "second": [
            {"code": "MCM302", "title": "Advertising Media Planning", "unit": 3},
            {"code": "MCM300", "title": "Research Project", "unit": 6},
            {"code": "MCM304", "title": "International Communication", "unit": 3},
            {"code": "MCM306", "title": "Freelance & Feature Writing", "unit": 3},
            {"code": "MCM308", "title": "Studio Management Techniques", "unit": 3},
            {"code": "MCM310", "title": "Telecom Technology & Policy", "unit": 3},
            {"code": "MCM312", "title": "Introduction to Social Psychology", "unit": 2},
            {"code": "MKT302", "title": "Integrated Marketing Communication", "unit": 2},
            {"code": "POL302", "title": "Contemporary International Politics", "unit": 3},
            {"code": "MCM314", "title": "Advertising & PR Campaign Strategies", "unit": 2},
        ]
    }
},

# ======================================================
# FACULTY OF SOCIAL SCIENCE
# ======================================================

"International Relations / Political Science": {

    100: {
        "first": [
            {"code": "GNS101", "title": "Use of English", "unit": 2},
            {"code": "GNS103", "title": "Introduction to Philosophy", "unit": 2},
            {"code": "GNS105", "title": "Basic Study Skills", "unit": 2},
            {"code": "ECN101", "title": "Introduction to Economics I", "unit": 2},
            {"code": "IRS101", "title": "Structure of International Society", "unit": 2},
            {"code": "IRS103", "title": "History of Europe (1300–1600)", "unit": 3},
            {"code": "CSC101", "title": "Introduction to Computer Science", "unit": 3},
            {"code": "IRS105", "title": "History of Africa (1500–1800)", "unit": 3},
            {"code": "IRS107", "title": "Introduction to International Relations", "unit": 3},
        ],

        "second": [
            {"code": "GNS102", "title": "Logic and Reasoning", "unit": 2},
            {"code": "GNS104", "title": "Politics and Government", "unit": 2},
            {"code": "GNS106", "title": "Literature in English", "unit": 2},
            {"code": "POL102", "title": "Introduction to Political Science", "unit": 3},
            {"code": "POL104", "title": "Organization of Government", "unit": 2},
            {"code": "IRS102", "title": "Theories of International Relations", "unit": 3},
            {"code": "IRS104", "title": "History of Europe (1700–1900)", "unit": 3},
            {"code": "IRS106", "title": "History of Africa (1800–1900)", "unit": 2},
            {"code": "IRS108", "title": "Introduction to Sociology", "unit": 2},
            {"code": "LIS102", "title": "Introduction to Libraries", "unit": 3},
        ]
    },

    200: {
        "first": [
            {"code": "IRS201", "title": "Introduction to Foreign Policy Analysis", "unit": 3},
            {"code": "POL201", "title": "Political Thought: Plato to Machiavelli", "unit": 3},
            {"code": "POL203", "title": "Political Behaviour", "unit": 3},
            {"code": "IRS203", "title": "Evolution and Development of Modern International System", "unit": 2},
            {"code": "IRS205", "title": "Europe and the World: Colonialism and Politics", "unit": 3},
            {"code": "IRS207", "title": "Africa and the International System", "unit": 3},
            {"code": "MTH203", "title": "Mathematical Methods for Social Science", "unit": 2},
            {"code": "ECO201", "title": "Microeconomics", "unit": 3},
        ],

        "second": [
            {"code": "IRS202", "title": "International Legal Order", "unit": 3},
            {"code": "IRS204", "title": "Politics of International Economic Relations", "unit": 3},
            {"code": "IRS206", "title": "International Organizations", "unit": 3},
            {"code": "POL202", "title": "Political Thought Since Hobbes", "unit": 3},
            {"code": "IRS208", "title": "Middle East Politics", "unit": 3},
            {"code": "IRS210", "title": "Technology, Ecology & World Affairs", "unit": 2},
            {"code": "IRS212", "title": "New States in World Politics", "unit": 2},
            {"code": "IRS214", "title": "Economic Integration in Africa", "unit": 3},
            {"code": "ECO202", "title": "Macroeconomics", "unit": 3},
        ]

    },
        300: {
        "first": [
            {"code": "IRS301", "title": "Theories of International Relations II", "unit": 3},
            {"code": "IRS303", "title": "Race and Ethnicity in International Relations", "unit": 3},
            {"code": "IRS305", "title": "Asia in World Politics", "unit": 3},
            {"code": "MCM/IRS321", "title": "Mass Media and Society", "unit": 3},
            {"code": "IRS309", "title": "Research Methodology", "unit": 2},
            {"code": "IRS311", "title": "Principles and Practices of Diplomacy", "unit": 3},
            {"code": "IRS313", "title": "America and the World", "unit": 3},
            {"code": "IRS315", "title": "Economic Integration in Europe", "unit": 3},
            {"code": "BUS303", "title": "International Business Environment", "unit": 2},
            {"code": "IRS399", "title": "Seminar / Independent Study", "unit": 2},
        ],

        "second": [
            {"code": "POL302", "title": "Contemporary World Politics", "unit": 3},
            {"code": "IRS304", "title": "Population & Migration Studies", "unit": 3},
            {"code": "IRS306", "title": "Strategic Studies", "unit": 3},
            {"code": "IRS308", "title": "Foreign Policies of Great Powers", "unit": 3},
            {"code": "IRS310", "title": "Nigeria–Benin Foreign Relations", "unit": 3},
            {"code": "IRS312", "title": "Chinese Economy", "unit": 3},
            {"code": "POL312", "title": "Negotiation & Diplomacy", "unit": 3},
            {"code": "IRS300", "title": "Research Project", "unit": 6},
            {"code": "PAD302", "title": "Public Administration", "unit": 2},
        ]
    }
},

    
# ======================================================
# FACULTY OF PURE & APPLIED SCIENCE – NURSING
# ======================================================

"Nursing Science": {

    100: {
        "first": [
            {"code": "BIO111", "title": "Human Biology", "unit": 3},
            {"code": "NSS101", "title": "Nature of Nursing", "unit": 3},
            {"code": "CSC101", "title": "Introduction to Computer", "unit": 3},
            {"code": "PHY101", "title": "General Physics", "unit": 2},
            {"code": "CHM101", "title": "General Chemistry", "unit": 2},
            {"code": "GNS101", "title": "Use of English", "unit": 2},
            {"code": "GNS105", "title": "Basic Study Skills", "unit": 2},
            {"code": "GNS103", "title": "Introduction to Philosophy", "unit": 2},
            {"code": "ECN101", "title": "Introduction to Economics", "unit": 2},
        ],

        "second": [
            {"code": "GNS106", "title": "Literature in English", "unit": 2},
            {"code": "GNS102", "title": "Logic and Reasoning", "unit": 2},
            {"code": "NSS104", "title": "Biostatistics I", "unit": 3},
            {"code": "NSS102", "title": "Family & Reproductive Health", "unit": 2},
            {"code": "NSS108", "title": "Nursing Care (ENT)", "unit": 3},
            {"code": "NSS110", "title": "Nutrition in Health & Disease", "unit": 3},
            {"code": "NSS112", "title": "Elementary Mathematics", "unit": 2},
            {"code": "NSS114", "title": "Human Anatomy & Physiology", "unit": 3},
            {"code": "CHM102", "title": "General Chemistry II", "unit": 2},
            {"code": "SOC102", "title": "Sociology & Anthropology", "unit": 2},
            {"code": "NSS106", "title": "Principles of Professional Nursing", "unit": 3},
            {"code": "LIS102", "title": "Introduction to Libraries", "unit": 3},
        ]

        
    },

    200: {
        "first": [
            {"code": "NSS201", "title": "Anatomy and Physiology", "unit": 3},
            {"code": "NSS211", "title": "Biochemistry", "unit": 2},
            {"code": "NSS213", "title": "Environmental Health", "unit": 2},
            {"code": "NSS217", "title": "Medical–Surgical Nursing", "unit": 3},
            {"code": "NSS209", "title": "Public Health", "unit": 3},
        ],

        "second": [
            {"code": "NSS202", "title": "Medical-Surgical Nursing II", "unit": 3},
            {"code": "NSS208", "title": "Primary Health Care (School Health)", "unit": 3},
            {"code": "NSS210", "title": "Nursing Ethics & Jurisprudence", "unit": 3},
            {"code": "NSS212", "title": "Health Programme Planning", "unit": 3},
            {"code": "NSS214", "title": "Occupational Health", "unit": 3},
            {"code": "NSS216", "title": "Introduction to Pharmacology", "unit": 3},
            {"code": "NSS218", "title": "Human Behaviour in Health & Disease", "unit": 3},
        ]
    },

    300: {
        "first": [
            {"code": "NSS317", "title": "Anatomy and Physiology", "unit": 3},
            {"code": "NSS303", "title": "Basic Pharmacology of Drugs", "unit": 3},
            {"code": "NSS301", "title": "Medical–Surgical Nursing III", "unit": 3},
            {"code": "NSS307", "title": "Community Health", "unit": 3},
            {"code": "NSS309", "title": "Midwifery", "unit": 3},
            {"code": "NSS313", "title": "Maternal and Child Health", "unit": 3},
        ],

        "second": [
            {"code": "NSS302", "title": "Pharmacology II", "unit": 3},
            {"code": "NSS304", "title": "Medical-Surgical Nursing IV", "unit": 3},
            {"code": "NSS308", "title": "Community Health II", "unit": 3},
            {"code": "NSS310", "title": "Midwifery II", "unit": 3},
            {"code": "NSS312", "title": "Maternal & Child Health Nursing II", "unit": 3},
            {"code": "NSS314", "title": "Primary Health Care Services", "unit": 2},
            {"code": "NSS316", "title": "Management Principles in Nursing", "unit": 2},
            {"code": "NSS318", "title": "Anatomy & Physiology", "unit": 3},
            {"code": "NSS320", "title": "Research Methods in Nursing I", "unit": 2},
            {"code": "MCB302", "title": "Immunology", "unit": 2},
        ]
    },

    400: {
        "first": [
            {"code": "NSS403", "title": "Orthopedic Nursing", "unit": 3},
            {"code": "NSS413", "title": "Epidemiology", "unit": 3},
            {"code": "NSS313", "title": "Maternal and Child Health", "unit": 3},
            {"code": "NSS301", "title": "Medical–Surgical Nursing III", "unit": 3},
            {"code": "NSS309", "title": "Midwifery", "unit": 3},
            {"code": "NSS419", "title": "Seminar / Independent Study", "unit": 3},
        ],

        "second": [
            {"code": "NSS402", "title": "Mental Health & Psychiatry", "unit": 3},
            {"code": "NSS404", "title": "Medical-Surgical Nursing VI", "unit": 2},
            {"code": "NSS406", "title": "Applied Medical Sociology", "unit": 2},
            {"code": "NSS408", "title": "Geriatric Nursing", "unit": 3},
            {"code": "NSS410", "title": "Pediatric Nursing", "unit": 3},
            {"code": "NSS412", "title": "Radiology & Radiotherapy Nursing", "unit": 2},
            {"code": "NSS414", "title": "ENT Nursing", "unit": 2},
            {"code": "NSS418", "title": "Anaesthetic Nursing", "unit": 3},
            {"code": "NSS416", "title": "Research Project", "unit": 6},
        ]
    }
}

}

COURSE_ALIASES = {
    "Accounting": "Accounting",
    "Economics": "Economics",
    "Human Resources Management": "Human Resources Management",
    "Business Administration": "Business Administration",
    "Banking and Finance": "Accounting, Banking & Finance, Business Admin, HRM, Economics",
    "International Relations": "International Relations / Political Science",
    "Political Science": "International Relations / Political Science",
}

FIRST_SEMESTER_PERCENT = 70
SECOND_SEMESTER_PERCENT = 100




# ================= CONFIG =================
SECRET_KEY = "CHANGE_THIS_SECRET_NOW"
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# ================= APP =================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= PATHS =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PHOTO_DIR = os.path.join(UPLOAD_DIR, "photos")
ADMISSION_DIR = os.path.join(UPLOAD_DIR, "admission")

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(ADMISSION_DIR, exist_ok=True)

for d in ["nin", "birth", "olevel", "passport", "transcript"]:
    os.makedirs(os.path.join(ADMISSION_DIR, d), exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")



# ================= DATABASE =================
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= HELPERS =================
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

TOTAL_SEMESTER_WEEKS = 12
MIN_PAYMENT = 45000
TRANSACTION_FEE = 1500
FIRST_SEMESTER_FULL_PERCENT = 70

def recalculate_access(student, db):
    if student.fees_total <= 0:
        student.access_percentage = 0
        student.accessible_weeks = 0
        return

    percent = (student.fees_paid / student.fees_total) * 100
    percent = min(round(percent, 1), 100)

    semester = get_current_semester(db)
    weeks = 0

    # ---------------- FIRST SEMESTER ----------------
    if semester == "first":
        if percent < 22.5:
            weeks = 0
        elif percent < 70:
            weeks = int((percent / 100) * TOTAL_SEMESTER_WEEKS)
        else:
            weeks = TOTAL_SEMESTER_WEEKS

    # ---------------- SECOND SEMESTER ----------------
    else:
        if percent < 80:
            weeks = 0
        elif percent < 100:
            weeks = 2
        else:
            weeks = TOTAL_SEMESTER_WEEKS

    student.access_percentage = percent
    student.accessible_weeks = min(weeks, TOTAL_SEMESTER_WEEKS)


def can_accept_payment(student, amount):
    remaining = student.fees_total - student.fees_paid

    if remaining <= 0:
        return False, "School fees already fully paid for this session"

    if amount > remaining:
        return False, f"Only ₦{remaining:,} remaining for this session"

    return True, None

def create_token(user_id: int, role: str):
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_user_from_token(auth: str | None, db: Session):
    if not auth:
        return None
    try:
        token = auth.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return db.query(User).filter(User.id == int(payload["sub"])).first()
    except:
        return None

def require_admin(
    Authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_user_from_token(Authorization, db)
    if not user or user.role != "admin":
        raise HTTPException(401, "Admin only")
    return user

def require_student(
    Authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_user_from_token(Authorization, db)
    if not user or user.role != "student":
        raise HTTPException(401, "Student only")
    return user

def grade_score(total):
    if total >= 70: return "A", "Excellent"
    if total >= 60: return "B", "Very Good"
    if total >= 50: return "C", "Good"
    if total >= 45: return "D", "Pass"
    return "F", "Fail"

def get_current_level(student_id: int, db: Session):
    rec = db.query(StudentLevel).filter_by(
        student_id=student_id,
        is_current=1
    ).first()
    return rec.level if rec else None


def ai_tutor_reply(question: str, course: str, lesson: str = ""):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a calm, friendly university lecturer teaching {course}. "
                        "Explain simply and clearly."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Lesson context:\n{lesson}\n\n"
                        f"Student question:\n{question}"
                    )
                }
            ],
            temperature=0.4
        )

        return response.choices[0].message.content

    except Exception as e:
        print("PROF. ALEX ELI:", e)
        return "⚠️ PROF. ALEX is currently unavailable. Please try again later."


def course_code_exists(code: str):
    for course_group in COURSE_REGISTRY.values():
        for level in course_group.values():
            for semester in level.values():
                if any(c["code"].upper() == code for c in semester):
                    return True
    return False

def normalize_course_code(code: str):
    return code.strip().upper()

def validate_course_code(code: str):
    code = normalize_course_code(code)

    if not course_code_exists(code):
        raise HTTPException(400, f"Unknown course code: {code}")

    return code

def course_belongs_to_semester(course_code, course_name, level, semester):
    course_key = COURSE_ALIASES.get(course_name, course_name)

    course_key = next(
        (k for k in COURSE_REGISTRY if k.lower() == course_key.lower()),
        None
    )
    if not course_key:
        return False

    return any(
        c["code"].upper() == course_code
        for c in COURSE_REGISTRY
            .get(course_key, {})
            .get(level, {})
            .get(semester, [])
    )


@app.post("/admin/register")
def admin_register_student(
    photo: UploadFile = File(None),
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    gender: str = Form(...),
    faculty: str = Form(...),
    course: str = Form(...),
    level: int = Form(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    # ================= NORMALIZE FACULTY =================
    faculty = faculty.upper().strip()

    if faculty not in FACULTY_FEES:
        raise HTTPException(400, "Invalid faculty selected")

    # ================= CHECK DUPLICATES =================
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already registered")

    # ================= GENERATE MATRIC =================
    year = datetime.now().year
    count = db.query(User).filter(User.role == "student").count() + 1
    matric_no = f"ELI/{year}/{count:04d}"

    # ================= TEMP PASSWORD =================
    temp_password = uuid.uuid4().hex[:8]

    # ================= PHOTO UPLOAD =================
    photo_path = None
    if photo:
        ext = photo.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        photo_path = f"uploads/photos/{filename}"

        with open(photo_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)

    # ================= FEES =================
    fees_total = FACULTY_FEES[faculty]

    # ================= CREATE STUDENT =================
    student = User(
        role="student",
        full_name=full_name,
        email=email,
        phone=phone,
        gender=gender,
        faculty=faculty,
        course=course.strip().title(),
        level=int(level),
        matric_no=matric_no,
        password_hash=hash_password(temp_password),
        fees_total=fees_total,
        fees_paid=0,
        access_percentage=0,
        accessible_weeks=0,
        photo=photo_path
    )

    db.add(student)
    db.commit()
    db.refresh(student)  # ✅ now student.id exists

    db.add(StudentLevel(
    student_id=student.id,
    level=int(level),
    session=f"{datetime.now().year}/{datetime.now().year + 1}",
    is_current=1
    ))
    db.commit()


    return {
        "message": "Student registered successfully",
        "matric_no": matric_no,
        "temp_password": temp_password
    }

# ================= DEFAULT ADMIN =================
def create_admin():
    db = SessionLocal()
    db.query(User).filter(User.email == "admin@elishalene.com").delete()
    admin = User(
        role="admin",
        full_name="School Administrator",
        email="admin@elishalene.com",
        password_hash=hash_password("Admin123")
    )
    db.add(admin)
    db.commit()
    db.close()

create_admin()

# ================= AUTH =================
class AdminLogin(BaseModel):
    email: str
    password: str

@app.post("/token")
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == data.email,
        User.role == "admin"
    ).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid admin login")

    return {"access_token": create_token(user.id, "admin")}

class StudentLogin(BaseModel):
    matric_no: str
    password: str

@app.post("/student/login")
def student_login(data: StudentLogin, db: Session = Depends(get_db)):
    student = db.query(User).filter(
        User.matric_no == data.matric_no,
        User.role == "student"
    ).first()

    if not student or not verify_password(data.password, student.password_hash):
        raise HTTPException(401, "Invalid login")

    return {"token": create_token(student.id, "student")}

# ================= SEMESTER =================
@app.post("/admin/set-semester")
def set_semester(
    semester: str = Form(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    if semester not in ["first", "second"]:
        raise HTTPException(400, "Invalid semester")

    cfg = db.query(AppConfig).first()
    old = cfg.active_semester if cfg else None

    if not cfg:
        cfg = AppConfig(active_semester=semester)
        db.add(cfg)
    else:
        if cfg.active_semester == semester:
            return {"message": "Semester already active"}
        cfg.active_semester = semester

    db.add(SemesterLog(
        old_semester=old,
        new_semester=semester,
        changed_by=admin.email
    ))

    db.commit()
    return {"message": f"Semester switched to {semester.upper()}"}

def get_current_semester(db: Session):
    cfg = db.query(AppConfig).first()
    return cfg.active_semester if cfg else "first"



@app.get("/student/me")
def student_me(
    student=Depends(require_student)
):
    return {
        "full_name": student.full_name,
        "matric_no": student.matric_no,
        "gender": student.gender,
        "faculty": student.faculty,   # ✅ FIXED
        "course": student.course,
        "level": student.level,
        "fees_paid": student.fees_paid,
        "fees_total": student.fees_total,
        "access_percentage": student.access_percentage,
        "accessible_weeks": student.accessible_weeks,
        "photo": (
            "/" + student.photo
            if student.photo
            else "/uploads/photos/default-avatar.png"
        )
    }


# ================= PAYMENT =================
@app.post("/student/pay")
def student_pay(
    amount: int = Form(...),
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    if amount < MIN_PAYMENT:
        raise HTTPException(
            400,
            f"Minimum payment per transaction is ₦{MIN_PAYMENT:,}"
        )

    allowed, msg = can_accept_payment(student, amount)
    if not allowed:
        raise HTTPException(400, msg)

    student.fees_paid += amount
    recalculate_access(student, db)
    db.commit()

    return {
        "message": "Payment successful",
        "amount": amount,
        "transaction_fee": TRANSACTION_FEE,
        "total_charged": amount + TRANSACTION_FEE,
        "fees_paid": student.fees_paid,
        "remaining": student.fees_total - student.fees_paid,
        "access_percentage": student.access_percentage,
        "accessible_weeks": student.accessible_weeks
    }


@app.post("/admin/update-payment")
def admin_update_payment(
    matric_no: str = Form(...),
    amount: int = Form(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    student = db.query(User).filter(
        User.matric_no == matric_no.strip().upper(),
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    allowed, msg = can_accept_payment(student, amount)
    if not allowed:
        raise HTTPException(400, msg)

    student.fees_paid += amount

    recalculate_access(student, db)
    db.commit()

    db.add(PaymentHistory(
        student_id=student.id,
        amount=amount,
        method="manual"
    ))
    db.commit()


    return {
        "message": "Payment updated",
        "fees_paid": student.fees_paid,
        "remaining": student.fees_total - student.fees_paid,
        "access_percentage": student.access_percentage,
        "accessible_weeks": student.accessible_weeks
    }


# ================= RESULTS =================
@app.post("/admin/upload-result")
def upload_result(
    matric_no: str = Form(...),
    course: str = Form(...),
    ca_score: int = Form(...),
    exam_score: int = Form(...),
    semester: str = Form(...),
    level: int = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    student = db.query(User).filter(User.matric_no == matric_no).first()
    if not student:
        raise HTTPException(404, "Student not found")

    total = ca_score + exam_score

    if total >= 70:
        grade, remark = "A", "Excellent"
    elif total >= 60:
        grade, remark = "B", "Very Good"
    elif total >= 50:
        grade, remark = "C", "Good"
    elif total >= 45:
        grade, remark = "D", "Pass"
    else:
        grade, remark = "F", "Fail"

    result = Result(
        student_id=student.id,
        course=course,
        ca_score=ca_score,
        exam_score=exam_score,
        total=total,
        grade=grade,
        remark=remark,
        semester=semester,
        level=level,
        session=str(datetime.now().year)
    )

    db.add(result)
    db.commit()

    return {"message": "Result uploaded"}



@app.get("/admin/results")
def admin_search_results(
    matric_no: str,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    matric_no = matric_no.strip().upper()

    student = db.query(User).filter(
        User.matric_no == matric_no,
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    results = db.query(Result).filter(
        Result.student_id == student.id
    ).order_by(Result.created_at.desc()).all()

    return results

@app.put("/admin/result/{id}")
def admin_update_result(
    id: int,
    ca: int = Form(...),
    exam: int = Form(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    result = db.query(Result).filter(Result.id == id).first()

    if not result:
        raise HTTPException(404, "Result not found")

    if ca < 0 or ca > 40 or exam < 0 or exam > 60:
        raise HTTPException(400, "Invalid CA or Exam score")

    total = ca + exam
    grade, remark = grade_score(total)

    result.ca_score = ca
    result.exam_score = exam
    result.total = total
    result.grade = grade
    result.remark = remark

    db.commit()

    return {
        "message": "Result updated successfully",
        "total": total,
        "grade": grade,
        "remark": remark
    }


@app.delete("/admin/result/{id}")
def delete_result(
    id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    result = db.query(Result).get(id)

    if not result:
        raise HTTPException(404, "Result not found")

    db.delete(result)
    db.commit()

    return {"message": "Result deleted"}




from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Image, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from fastapi.responses import FileResponse
import os

@app.get("/student/results/pdf")
def student_results_pdf(
    level: int,
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    results = db.query(Result).filter(
        Result.student_id == student.id,
        Result.level == level
    ).order_by(Result.semester, Result.course).all()

    if not results:
        raise HTTPException(404, "No results found")

    # -------- GROUP BY SEMESTER --------
    sem_results = {"first": [], "second": []}
    for r in results:
        sem = (r.semester or "").strip().lower()
        if sem in sem_results:
            sem_results[sem].append(r)

    # -------- GPA --------
    GRADE_POINTS = {"A":5,"B":4,"C":3,"D":2,"E":1,"F":0}

    def calc_gpa(res):
        if not res:
            return 0
        return round(
            sum(GRADE_POINTS.get(r.grade, 0) for r in res) / len(res),
            2
        )

    gpa_first = calc_gpa(sem_results["first"])
    gpa_second = calc_gpa(sem_results["second"])
    cgpa = calc_gpa(results)

    # -------- PDF SETUP --------
    filename = f"Academic_Result_L{level}.pdf"
    path = os.path.join("uploads", filename)

    doc = SimpleDocTemplate(path, pagesize=A4)

    # ✅ DEFINE STYLES FIRST
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.green
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        textColor=colors.red
    )

    center_normal = ParagraphStyle(
        "CenterNormal",
        parent=styles["Normal"],
        alignment=TA_CENTER
    )

    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9
    )

    elements = []

    # -------- LOGO --------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    logo_path = os.path.join(BASE_DIR, "school-logo.jpeg")

    print("LOGO ABS PATH:", logo_path)

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=90, height=90)
        logo.hAlign = "CENTER"
        elements.append(logo)
    else:
        raise Exception(f"Logo not found at {logo_path}")


    elements.append(Spacer(1, 10))

    # -------- HEADER --------
    elements.append(Paragraph("ELISHA LENE INSTITUTE", title_style))
    elements.append(Paragraph("ACADEMIC RESULT", subtitle_style))
    elements.append(Spacer(1, 16))

    # -------- STUDENT INFO (ONLY ONCE) --------
    elements.append(Paragraph(
        f"""
        <b>Name:</b> {student.full_name}<br/>
        <b>Matric No:</b> {student.matric_no}<br/>
        <b>Faculty:</b> {student.faculty}<br/>
        <b>Course:</b> {student.course}<br/>
        <b>Level:</b> {level}
        """,
        center_normal
    ))
    elements.append(Spacer(1, 20))

    # -------- TABLE FUNCTION --------
    def semester_table(title, res, gpa):
        elements.append(Paragraph(f"{title} Semester", styles["Heading3"]))
        elements.append(Spacer(1, 6))

        if not res:
            elements.append(Paragraph("No results", styles["Normal"]))
            elements.append(Spacer(1, 12))
            return

        data = [
            ["Course", "CA", "Exam", "Total", "Grade"]
        ]

        for r in res:
            color = colors.green if r.total >= 50 else colors.red
            data.append([
                r.course,
                Paragraph(str(r.ca_score), ParagraphStyle("ca", textColor=color)),
                Paragraph(str(r.exam_score), ParagraphStyle("ex", textColor=color)),
                Paragraph(str(r.total), ParagraphStyle("tot", textColor=color)),
                r.grade
            ])

        table = Table(data, colWidths=[100, 50, 50, 50, 50])
        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"GPA: {gpa}", center_normal))
        elements.append(Spacer(1, 18))

    # ✅ CALL THE TABLES (YOU WERE MISSING THIS)
    semester_table("First", sem_results["first"], gpa_first)
    semester_table("Second", sem_results["second"], gpa_second)

    # -------- CGPA --------
    elements.append(Paragraph(f"CGPA: {cgpa}", subtitle_style))
    elements.append(Spacer(1, 30))

    # -------- FOOTER --------
    elements.append(Paragraph("Powered by Elicoin", footer_style))

    doc.build(elements)

    return FileResponse(
        path,
        media_type="application/pdf",
        filename="Academic_Result.pdf"
    )




@app.get("/student/results")
def student_results(student=Depends(require_student), db: Session = Depends(get_db)):
    
    return db.query(Result)\
        .filter(Result.student_id == student.id)\
        .order_by(Result.level, Result.semester)\
        .all()
# ================= GPA =================
GRADE_POINTS = {"A":5,"B":4,"C":3,"D":2,"E":1,"F":0}

@app.get("/api/student/gpa")
def student_gpa(
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    results = db.query(Result).filter(
        Result.student_id == student.id
    ).all()

    if not results:
        return {
            "has_results": False,
            "gpa": None,
            "cgpa": None
        }

    GRADE_POINTS = {"A":5,"B":4,"C":3,"D":2,"E":1,"F":0}

    def calc(res):
        return round(
            sum(GRADE_POINTS.get(r.grade, 0) for r in res) / len(res),
            2
        )

    first = [r for r in results if r.semester == "first"]
    second = [r for r in results if r.semester == "second"]

    return {
        "has_results": True,
        "gpa": calc(first) if first else None,
        "cgpa": calc(results)
    }

@app.get("/student/payments")
def student_payments(student=Depends(require_student), db: Session = Depends(get_db)):
    payments = db.query(PaymentHistory)\
        .filter(PaymentHistory.student_id == student.id)\
        .order_by(PaymentHistory.created_at.desc())\
        .all()

    return [
        {
            "id": p.id,
            "amount": p.amount,
            "method": p.method,
            "reference": p.reference,
            "time": p.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for p in payments
    ]

@app.get("/student/receipt/{payment_id}")
def download_receipt(payment_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    pay = db.query(PaymentHistory).filter_by(id=payment_id, student_id=student.id).first()
    if not pay:
        raise HTTPException(404, "Receipt not found")

    filename = f"receipt_{pay.id}.pdf"
    path = os.path.join("uploads", filename)

    # PDF Settings
    doc = SimpleDocTemplate(path, pagesize=A4, rightMargin=40, leftMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    # === LOGO SECTION ===
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(BASE_DIR, "school-logo.jpeg")

    if os.path.exists(logo_path):
        from reportlab.platypus import Image
        logo = Image(logo_path, width=90, height=90)
        logo.hAlign = "CENTER"
        elements.append(logo)

    # === TITLES ===
    elements.append(Paragraph("<b>ELISHA LENE INSTITUTE</b>", styles["Title"]))
    elements.append(Paragraph("<b>PAYMENT RECEIPT</b>", styles["Heading2"]))
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # === STUDENT INFO ===
    elements.append(Paragraph(f"<b>Name:</b> {student.full_name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Matric No:</b> {student.matric_no}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Faculty:</b> {student.faculty}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Department:</b> {student.course}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Level:</b> {student.level}", styles["Normal"]))
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # === PAYMENT INFO ===
    elements.append(Paragraph(f"<b>Amount Paid:</b> ₦{pay.amount:,}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Method:</b> {pay.method.title()}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Reference:</b> {pay.reference or 'N/A'}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date:</b> {pay.created_at.strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # === FOOTER ===
    elements.append(Paragraph("<b>Powered by Elicoin</b>", styles["Normal"]))

    doc.build(elements)

    return FileResponse(path, filename=f"receipt_{pay.id}.pdf")



# ================= ANALYTICS =================
@app.get("/admin/analytics/results")
def analytics(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return {
        "total_students": db.query(User).filter(User.role=="student").count(),
        "total_results": db.query(Result).count(),
        "average_score": round(db.query(func.avg(Result.total)).scalar() or 0,2)
    }

@app.get("/admin/faculties")
def get_faculties(admin=Depends(require_admin)):
    return FACULTY_COURSES

@app.get("/student/active-semester")
def student_active_semester(
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    semester = get_current_semester(db)
    return {"semester": semester}


@app.get("/admin/student")
def admin_get_student(
    matric_no: str,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    matric_no = matric_no.strip().upper()  # ✅ FIX

    student = db.query(User).filter(
        User.matric_no == matric_no,
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    return {
        "full_name": student.full_name,
        "gender": student.gender,
        "faculty": student.faculty,
        "course": student.course,
        "level": student.level,
        "photo": "/" + student.photo if student.photo else "/uploads/photos/default-avatar.png"
    }


@app.put("/admin/student")
def admin_update_student(
    matric_no: str = Form(...),
    full_name: str = Form(...),
    gender: str = Form(...),
    faculty: str = Form(...),
    course: str = Form(...),
    level: int = Form(...),
    photo: UploadFile = File(None),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    matric_no = matric_no.strip().upper()
    faculty = faculty.upper().strip()

    student = db.query(User).filter(
        User.matric_no == matric_no,
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    if faculty not in FACULTY_FEES:
        raise HTTPException(400, "Invalid faculty")

    # ✅ BASIC UPDATE
    student.full_name = full_name
    student.gender = gender
    student.faculty = faculty
    student.course = course.strip().title()
    student.level = level

    # ✅ UPDATE FEES BASED ON FACULTY
    student.fees_total = FACULTY_FEES[faculty]

    # ✅ RECALCULATE ACCESS
    percent = int((student.fees_paid / student.fees_total) * 100)
    percent = min(percent, 100)

    weeks = int((percent / 100) * TOTAL_SEMESTER_WEEKS)

    student.access_percentage = percent
    student.accessible_weeks = weeks

    # ✅ PHOTO
    if photo:
        ext = photo.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        path = f"uploads/photos/{filename}"
        with open(path, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        student.photo = path

    db.commit()

    return {
        "message": "Student updated successfully",
        "fees_total": student.fees_total,
        "fees_paid": student.fees_paid,
        "access_percentage": student.access_percentage,
        "accessible_weeks": student.accessible_weeks
    }

@app.get("/student/course-form")
def course_form(
    semester: str | None = None,
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    # ================= RESOLVE SEMESTER & SESSION =================
    active_semester = semester or get_current_semester(db)
    current_session = f"{datetime.now().year}/{datetime.now().year + 1}"

    # ================= ENFORCE COURSE FORM PAYMENT =================
    payment = db.query(CourseFormPayment).filter_by(
        student_id=student.id,
        semester=active_semester,
        session=current_session
    ).first()

    if not payment or not payment.paid:
        raise HTTPException(
            403,
            "Course form not paid for this semester"
        )

    # ================= SAFE COURSE LOOKUP =================
    course_name = COURSE_ALIASES.get(student.course, student.course)

    course_key = next(
        (k for k in COURSE_REGISTRY if k.lower() == course_name.lower()),
        None
    )

    if not course_key:
        raise HTTPException(400, "Course not configured")

    levels = COURSE_REGISTRY[course_key]

    # ================= LEVEL CHECK =================
    try:
        level = int(student.level)
    except:
        raise HTTPException(400, "Invalid student level")

    if level not in levels:
        raise HTTPException(400, "Level not configured")

    semesters = levels[level]

    if active_semester not in semesters:
        raise HTTPException(
            400,
            f"No courses for {active_semester} semester"
        )

    courses = semesters[active_semester]

    # ================= GENERATE PDF =================
    file_path = (
        f"uploads/course_form_"
        f"{student.matric_no.replace('/', '_')}_"
        f"{active_semester}_"
        f"{current_session.replace('/', '-')}.pdf"
    )

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("<b>ELISHA LENE INSTITUTE</b>", styles["Title"]),
        Paragraph(f"Name: {student.full_name}", styles["Normal"]),
        Paragraph(f"Matric No: {student.matric_no}", styles["Normal"]),
        Paragraph(f"Course: {course_key}", styles["Normal"]),
        Paragraph(f"Level: {level}", styles["Normal"]),
        Paragraph(f"Semester: {active_semester.upper()}", styles["Normal"]),
        Paragraph(f"Session: {current_session}", styles["Normal"]),
        Paragraph("<br/>", styles["Normal"]),
    ]

    table_data = [["Code", "Course Title", "Unit"]]
    for c in courses:
        table_data.append([
            c["code"],
            c["title"],
            str(c["unit"])
        ])

    table = Table(table_data, colWidths=[90, 280, 60])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (2, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(table)
    doc.build(elements)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="course_form.pdf"
    )



@app.get("/student/course-content/{course_code}")
def get_course_content(
    course_code: str,
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    TOTAL_WEEKS = TOTAL_SEMESTER_WEEKS  # 12

    # 🔐 BACKEND IS THE BOSS
    unlocked_weeks = student.accessible_weeks or 0

    # Safety clamp
    unlocked_weeks = max(0, min(unlocked_weeks, TOTAL_WEEKS))

    # Fetch stored content (if any)
    contents = db.query(CourseContent).filter(
        CourseContent.course_code == course_code
    ).order_by(CourseContent.week).all()

    weeks = []

    for week_num in range(1, TOTAL_WEEKS + 1):
        content = next((c for c in contents if c.week == week_num), None)

        weeks.append({
            "week": week_num,
            "title": content.title if content else f"Week {week_num}",
            "locked": week_num > unlocked_weeks
        })

    return {
        "total_weeks": TOTAL_WEEKS,
        "unlocked_weeks": unlocked_weeks,
        "access_percentage": student.access_percentage,
        "weeks": weeks
    }


@app.get("/student/course-list")
def student_course_list(
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    semester = get_current_semester(db)

# 🔐 BLOCK SECOND SEMESTER IF NOT FULLY PAID
    if semester == "second" and student.access_percentage < 100:
        return {
         "semester": semester,
         "locked": True,
         "message": "Complete school fees to access second semester",
            "courses": []
    }


    # ---- normalize course ----
    raw_course = student.course.strip()
    course_name = COURSE_ALIASES.get(raw_course, raw_course)

    course_key = next(
        (k for k in COURSE_REGISTRY if k.lower() == course_name.lower()),
        None
    )

    if not course_key:
        return {
            "semester": semester,
            "course": raw_course,
            "level": student.level,
            "courses": []
        }

    # ---- normalize level ----
    try:
        level = int(student.level)
    except:
        return {
            "semester": semester,
            "course": course_key,
            "level": student.level,
            "courses": []
        }

    levels = COURSE_REGISTRY[course_key]

    if level not in levels:
        return {
            "semester": semester,
            "course": course_key,
            "level": level,
            "courses": []
        }

    courses = levels[level].get(semester, [])

    return {
        "semester": semester,
        "course": course_key,
        "level": level,
        "courses": courses
    }


@app.post("/admin/course-form/pay")
def admin_mark_course_form_paid(
    matric_no: str = Form(...),
    semester: str = Form(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    semester = semester.lower()
    if semester not in ["first", "second"]:
        raise HTTPException(400, "Invalid semester")

    student = db.query(User).filter(
        User.matric_no == matric_no.strip().upper(),
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    session = f"{datetime.now().year}/{datetime.now().year + 1}"

    payment = db.query(CourseFormPayment).filter_by(
        student_id=student.id,
        semester=semester,
        session=session
    ).first()

    if not payment:
        payment = CourseFormPayment(
            student_id=student.id,
            semester=semester,
            session=session,
            paid=1
        )
        db.add(payment)
    else:
        payment.paid = 1

    db.commit()

    return {
        "message": f"Course form marked as PAID for {semester.upper()} semester",
        "student": student.matric_no,
        "semester": semester,
        "session": session
    }

@app.get("/student/course-form/status")
def course_form_status(
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    semester = get_current_semester(db)
    session = f"{datetime.now().year}/{datetime.now().year + 1}"

    payment = db.query(CourseFormPayment).filter_by(
        student_id=student.id,
        semester=semester,
        session=session
    ).first()

    return {
        "paid": bool(payment and payment.paid),
        "semester": semester,
        "session": session
    }
@app.post("/admin/promote-student")
def promote_student(
    matric_no: str = Form(...),
    new_level: int = Form(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    student = db.query(User).filter(
        User.matric_no == matric_no.strip().upper(),
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    session = f"{datetime.now().year}/{datetime.now().year + 1}"

    # Deactivate old level
    db.query(StudentLevel).filter_by(
        student_id=student.id,
        is_current=1
    ).update({"is_current": 0})

    # Insert new level
    db.add(StudentLevel(
        student_id=student.id,
        level=new_level,
        session=session,
        is_current=1
    ))

    # Update display-only level
    student.level = new_level

    # RESET FEES & ACCESS FOR NEW SESSION
    student.fees_paid = 0
    student.access_percentage = 0
    student.accessible_weeks = 0

    db.commit()

    return {
        "message": "Student promoted successfully",
        "student": student.matric_no,
        "new_level": new_level,
        "session": session
    }

@app.get("/student/transcript")
def download_transcript(
    session: str | None = None,
    level: int | None = None,
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    # ================= DETERMINE SESSION & LEVEL =================
    current_year = datetime.now().year
    active_session = session or f"{current_year}/{current_year + 1}"

    try:
        active_level = level or int(student.level)
    except:
        raise HTTPException(400, "Invalid level")

    # ================= FETCH RESULTS =================
    results = db.query(Result).filter(
        Result.student_id == student.id,
        Result.session == active_session,
        Result.level == active_level
    ).order_by(Result.semester).all()

    if not results:
        raise HTTPException(
            404,
            "No results found for selected session and level"
        )

    # ================= GROUP BY SEMESTER =================
    sem_results = {"first": [], "second": []}
    for r in results:
        sem_results[r.semester].append(r)

    # ================= GPA CALCULATION =================
    def calc_gpa(res):
        if not res:
            return 0
        points = [GRADE_POINTS.get(r.grade, 0) for r in res]
        return round(sum(points) / len(points), 2)

    gpa_first = calc_gpa(sem_results["first"])
    gpa_second = calc_gpa(sem_results["second"])

    # ================= CGPA (ALL TIME) =================
    all_results = db.query(Result).filter(
        Result.student_id == student.id
    ).all()

    cgpa = (
        round(
            sum(GRADE_POINTS.get(r.grade, 0) for r in all_results) / len(all_results),
            2
        )
        if all_results else 0
    )

    # ================= PDF PATH =================
    safe_session = active_session.replace("/", "-")
    file_path = (
        f"uploads/transcript_"
        f"{student.matric_no.replace('/', '_')}_"
        f"L{active_level}_"
        f"{safe_session}.pdf"
    )

    # ================= BUILD PDF =================
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # ---------- HEADER ----------
    elements.append(Paragraph("<b>ELISHA LENE INSTITUTE</b>", styles["Title"]))
    elements.append(Paragraph("<b>OFFICIAL ACADEMIC TRANSCRIPT</b>", styles["Heading2"]))
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # ---------- STUDENT INFO ----------
    elements.extend([
        Paragraph(f"<b>Name:</b> {student.full_name}", styles["Normal"]),
        Paragraph(f"<b>Matric No:</b> {student.matric_no}", styles["Normal"]),
        Paragraph(f"<b>Faculty:</b> {student.faculty}", styles["Normal"]),
        Paragraph(f"<b>Course:</b> {student.course}", styles["Normal"]),
        Paragraph(f"<b>Session:</b> {active_session}", styles["Normal"]),
        Paragraph(f"<b>Level:</b> {active_level}", styles["Normal"]),
        Paragraph("<br/>", styles["Normal"]),
    ])

    # ================= SEMESTER TABLE BUILDER =================
    def semester_table(title, res, gpa):
        if not res:
            elements.append(
                Paragraph(f"<b>{title} Semester:</b> No results", styles["Normal"])
            )
            elements.append(Paragraph("<br/>", styles["Normal"]))
            return

        elements.append(Paragraph(f"<b>{title} Semester</b>", styles["Heading3"]))

        data = [["Course", "CA", "Exam", "Total", "Grade"]]
        for r in res:
            data.append([
                r.course,
                str(r.ca_score),
                str(r.exam_score),
                str(r.total),
                r.grade
            ])

        table = Table(data, colWidths=[90, 50, 50, 50, 50])
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ]))

        elements.append(table)
        elements.append(Paragraph(f"<b>GPA:</b> {gpa}", styles["Normal"]))
        elements.append(Paragraph("<br/>", styles["Normal"]))

    # ---------- FIRST SEMESTER ----------
    semester_table("First", sem_results["first"], gpa_first)

    # ---------- SECOND SEMESTER ----------
    semester_table("Second", sem_results["second"], gpa_second)

    # ---------- CGPA ----------
    elements.append(Paragraph(f"<b>Cumulative GPA (CGPA):</b> {cgpa}", styles["Heading3"]))

    # ---------- FOOTER ----------
    elements.append(Paragraph("<br/>", styles["Normal"]))
    elements.append(Paragraph(
        "This transcript is issued for official academic purposes only.",
        styles["Italic"]
    ))

    doc.build(elements)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="academic_transcript.pdf"
    )
    
@app.get("/admin/student/{matric}/course-list")
def admin_student_course_list(
    matric: str,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    student = db.query(User).filter(
        User.matric_no == matric.strip().upper(),
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    semester = get_current_semester(db)
    level = int(student.level)

    raw_course = student.course.strip()
    course_name = COURSE_ALIASES.get(raw_course, raw_course)

    course_key = next(
        (k for k in COURSE_REGISTRY if course_name.lower() in k.lower()),
        None
    )

    if not course_key:
        return {"courses": []}

    courses = (
        COURSE_REGISTRY
        .get(course_key, {})
        .get(level, {})
        .get(semester, [])
    )

    return {
        "courses": [c["code"].upper() for c in courses]
    }



@app.post("/admin/fix-access")
def fix_access(admin=Depends(require_admin), db: Session = Depends(get_db)):
    students = db.query(User).filter(User.role == "student").all()

    for s in students:
        recalculate_access(s, db)

    db.commit()
    return {"message": "Access recalculated for all students"}


@app.get("/student/classroom/{course_code}/{week}")
def get_classroom(course_code: str, week: int, student=Depends(require_student), db: Session = Depends(get_db)):
    course_code = validate_course_code(course_code)



    # ---------- VALIDATE WEEK ----------
    if week < 1 or week > TOTAL_SEMESTER_WEEKS:
        raise HTTPException(400, "Invalid week")

    # ---------- ACCESS CONTROL ----------
    if week > (student.accessible_weeks or 0):
        raise HTTPException(403, "Class is locked. Complete payment.")

    # ---------- FETCH CONTENT ----------
    content = db.query(CourseContent).filter_by(
        course_code=normalize_course_code(course_code),
        week=week
    ).first()


        # 🔐 ENSURE COURSE BELONGS TO STUDENT
    raw_course = student.course.strip()
    course_name = COURSE_ALIASES.get(raw_course, raw_course)

    course_key = next(
        (k for k in COURSE_REGISTRY if k.lower() == course_name.lower()),
        None
    )

    if not course_key:
        raise HTTPException(403, "Invalid course")

    semester = get_current_semester(db)
    level = int(student.level)

    allowed = COURSE_REGISTRY[course_key].get(level, {}).get(semester, [])
    allowed_codes = [c["code"].upper() for c in allowed]

    if course_code.upper() not in allowed_codes:
        raise HTTPException(403, "Course not assigned to you")


    # 🟢 AUTO MARK ATTENDANCE
    semester = get_current_semester(db)
    session = f"{datetime.now().year}/{datetime.now().year + 1}"

    already = db.query(Attendance).filter_by(
        student_id=student.id,
        course_code=course_code,
        week=week,
        semester=semester,
        session=session
    ).first()

    if not already:
        db.add(Attendance(
            student_id=student.id,
            course_code=course_code,
            week=week,
            semester=semester,
            session=session
        ))
        db.commit()


    return {
    "course": course_code,
    "week": week,
    "title": content.title if content else f"Week {week}",
    "content": content.content if content else "No lesson yet",
    "audio": content.audio if content else None,
    "pdf": content.pdf if content else None
}

@app.get("/student/classroom/{course_code}/{week}/chat")
def get_class_chat(
    course_code: str,
    week: int,
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    # ---------- ACCESS CHECK ----------
    if week > (student.accessible_weeks or 0):
        raise HTTPException(403, "Class locked")

    messages = db.query(ClassMessage).filter_by(
        course_code=course_code,
        week=week
    ).order_by(ClassMessage.created_at).all()

    return [
        {
            "sender": m.sender_name,
            "role": m.sender_role,
            "message": m.message,
            "time": m.created_at.strftime("%H:%M")
        }
        for m in messages
    ]
 
@app.post("/student/classroom/chat")
def post_chat(data: dict, Authorization: str = Header(...)):
    db = SessionLocal()

    payload = jwt.decode(
        Authorization.split()[1],
        SECRET_KEY,
        algorithms=["HS256"]
    )

    student = db.query(User).get(int(payload["sub"]))
    student_name = student.full_name

    course = data["course"]
    week = data["week"]
    message = data["message"]

    # Save student message
    db.add(ClassMessage(
        course_code=course,
        week=week,
        sender_role="student",
        sender_name=student_name,
        message=message
    ))
    db.commit()

        # 🔐 verify student is allowed this course
    allowed = db.query(CourseContent).filter_by(
        course_code=course,
        week=week
    ).first()

    if not allowed:
        db.close()
        raise HTTPException(403, "Invalid class")


    # AI reply
    lesson = db.query(CourseContent).filter_by(
        course_code=course,
        week=week
    ).first()

    try:
        ai_reply = ai_tutor_reply(
            message,
            course,
            lesson.content if lesson else ""
        )
    except Exception as e:
        ai_reply = (
            "⚠️ PROF. ALEX is temporarily unavailable. "
            "Your message has been recorded."
        )


    db.add(ClassMessage(
        course_code=course,
        week=week,
        sender_role="ai",
        sender_name="PROF. ALEX ELI",
        message=ai_reply
    ))
    db.commit()
    db.close()
    return {"status": "ok"}


@app.post("/admin/classroom/chat")
def admin_send_message(
    course: str = Form(...),
    week: int = Form(...),
    message: str = Form(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    db.add(ClassMessage(
        course_code=course,
        week=week,
        sender_role="admin",
        sender_name="Lecturer",
        message=message
    ))
    db.commit()
    return {"message": "Admin message sent"}

@app.get("/admin/classroom/{course_code}/{week}/chat")
def admin_get_class_chat(
    course_code: str,
    week: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    messages = db.query(ClassMessage).filter_by(
        course_code=course_code,
        week=week
    ).order_by(ClassMessage.created_at).all()

    return [
        {
            "sender": m.sender_name,
            "role": m.sender_role,
            "message": m.message,
            "time": m.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for m in messages
    ]

@app.post("/student/attendance")
def mark_attendance(
    course_code: str = Form(...),
    week: int = Form(...),
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    # 🔒 WEEK ACCESS CHECK
    if week > (student.accessible_weeks or 0):
        raise HTTPException(403, "Week locked")

    semester = get_current_semester(db)
    session = f"{datetime.now().year}/{datetime.now().year + 1}"

    # ❌ Prevent duplicate attendance
    exists = db.query(Attendance).filter_by(
        student_id=student.id,
        course_code=course_code,
        week=week,
        semester=semester,
        session=session
    ).first()

    if exists:
        return {"message": "Already marked present"}

    record = Attendance(
        student_id=student.id,
        course_code=course_code,
        week=week,
        semester=semester,
        session=session
    )

    db.add(record)
    db.commit()

    return {"message": "Attendance recorded"}

@app.get("/admin/attendance")
def view_attendance(
    course_code: str,
    week: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    records = db.query(Attendance).filter_by(
        course_code=course_code,
        week=week
    ).all()

    return [
    {
        "matric": db.query(User).get(r.student_id).matric_no,
        "time": r.attended_at.strftime("%Y-%m-%d %H:%M")
    }
    for r in records
]

@app.post("/admin/course-content")
def upload_course_content(
    course_code: str = Form(...),
    faculty: str = Form(...),
    level: int = Form(...),
    semester: str = Form(...),
    week: int = Form(...),
    title: str = Form(...),
    content: str = Form(""),
    pdf: UploadFile = File(None),
    audio: UploadFile = File(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    course_code = validate_course_code(course_code)
    pdf_path = None
    audio_path = None

    if pdf:
        pdf_name = f"{uuid.uuid4()}_{pdf.filename}"
        pdf_path = f"uploads/{pdf_name}"
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(pdf.file, f)

    if audio:
        audio_name = f"{uuid.uuid4()}_{audio.filename}"
        audio_path = f"uploads/{audio_name}"
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

    class_item = CourseContent(
        course_code=course_code.upper(),
        faculty=faculty,
        level=level,
        semester=semester,
        week=week,
        title=title,
        content=content,
        pdf=pdf_path,
        audio=audio_path
    )

    db.add(class_item)
    db.commit()

    return {"message": "Class uploaded successfully"}


@app.delete("/admin/course-content/{id}")
def delete_course_content(
    id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    cls = db.query(CourseContent).get(id)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    db.delete(cls)
    db.commit()
    return {"message": "Class deleted"}

@app.post("/student/class-replay")
def track_replay(data: dict, token: str = Header(...)):
    payload = jwt.decode(token.split()[1], SECRET_KEY, algorithms=["HS256"])

    db = SessionLocal()

    record = db.query(ClassReplay).filter_by(
        student_id = int(payload["sub"]),
        course_code=data["course"],
        week=data["week"]
    ).first()

    if not record:
        record = ClassReplay(
            student_id=int(payload["sub"]),
            course_code=data["course"],
            week=data["week"]
        )
        db.add(record)

    record.seconds_spent += data.get("seconds", 0)
    record.replay_count += 1
    record.last_seen = datetime.utcnow()

    db.commit()
    db.close()
    return {"status": "tracked"}


@app.get("/admin/weekly-classes")
def get_weekly_classes(
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    classes = db.query(CourseContent).order_by(
        CourseContent.course_code,
        CourseContent.week
    ).all()

    return [
        {
            "id": c.id,
            "course": c.course_code,
            "week": c.week,
            "title": c.title
        }
        for c in classes
    ]


@app.get("/student/classes")
def student_available_classes(
    week: int,
    student=Depends(require_student),
    db: Session = Depends(get_db),
):
    semester = get_current_semester(db)

    # 🔐 week access check
    if week > (student.accessible_weeks or 0):
        raise HTTPException(403, "Week locked")

    classes = (
        db.query(CourseContent)
        .filter(
            CourseContent.faculty == student.faculty,
            CourseContent.level == student.level,
            CourseContent.semester == semester,
            CourseContent.week == week
        )
        .order_by(CourseContent.course_code)
        .all()
    )

    return [
        {
            "course": c.course_code,
            "week": c.week,
            "title": c.title
        }
        for c in classes
    ]



@app.get("/student/summary")
def student_summary(student=Depends(require_student)):
    total_weeks = TOTAL_SEMESTER_WEEKS
    unlocked = student.accessible_weeks or 0

    return {
        "total_weeks": total_weeks,
        "accessible_weeks": unlocked,
        "completed": unlocked >= total_weeks,
        "certificate_eligible": unlocked >= total_weeks
    }

@app.post("/admin/reset-password")
def admin_reset_password(
    matric_no: str = Form(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    student = db.query(User).filter(
        User.matric_no == matric_no.strip().upper(),
        User.role == "student"
    ).first()

    if not student:
        raise HTTPException(404, "Student not found")

    new_password = uuid.uuid4().hex[:8]
    student.password_hash = hash_password(new_password)
    db.commit()

    return {
        "message": "Password reset successful",
        "new_password": new_password
    }

MIN_PAYMENT = 45000
TRANSACTION_FEE = 1565

@app.post("/student/flutterwave/init")
def flutterwave_init(
    amount: int = Form(...),
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    if amount < MIN_PAYMENT:
        raise HTTPException(400, f"Minimum payment is ₦{MIN_PAYMENT:,}")

    total_amount = amount + TRANSACTION_FEE

    url = "https://api.flutterwave.com/v3/payments"

    payload = {
        "tx_ref": f"ELI-{student.id}-{int(datetime.utcnow().timestamp())}",
        "amount": total_amount,
        "currency": "NGN",
        "redirect_url": "https://elinstitute.site/admission-form.html",

        "customer": {
            "email": student.email,
            "name": student.full_name,
        },
        "meta": {
            "student_id": student.id,
            "matric_no": student.matric_no,
            "school_amount": amount,
            "charge": TRANSACTION_FEE
        }
    }

    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(url, json=payload, headers=headers)
    data = r.json()

    if data.get("status") != "success":
        print("FLUTTERWAVE ERROR:", data)
        raise HTTPException(400, "Flutterwave initialization failed")

    # Flutterwave returns payment link
    return {"authorization_url": data["data"]["link"]}

@app.get("/student/flutterwave/verify")
def verify_flutterwave_payment(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {"Authorization": f"Bearer {FLW_SECRET_KEY}"}

    r = requests.get(url, headers=headers)
    data = r.json()

    if data.get("status") != "success":
        raise HTTPException(400, "Verification failed")

    trx = data["data"]

    if trx["status"] != "successful":
        raise HTTPException(400, "Transaction unsuccessful")

    meta = trx["meta"]
    student_id = meta["student_id"]
    school_amount = meta["school_amount"]

    student = db.query(User).get(student_id)

    if not student:
        raise HTTPException(404, "Student not found")

    # update school fees
    student.fees_paid += school_amount
    recalculate_access(student, db)
    db.commit()

    db.add(PaymentHistory(
        student_id=student.id,
        amount=school_amount,
        method="flutterwave",
        reference=transaction_id,
    ))
    db.commit()

    return {
        "message": "Payment verified successfully",
        "fees_paid": student.fees_paid,
        "access_percentage": student.access_percentage,
        "accessible_weeks": student.accessible_weeks
    }


@app.post("/admission/pay")
def admission_pay(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    amount = 15000  # Application fee

    payload = {
        "tx_ref": f"ADM-{uuid.uuid4()}",
        "amount": str(amount),
        "currency": "NGN",
        "redirect_url": "https://elinstitute.site/admission-form.html",
        "customer": {
            "email": email,
            "name": full_name,
            "phonenumber": phone
        },
        "meta": {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "application_fee": amount
        }
    }

    r = requests.post(
        "https://api.flutterwave.com/v3/payments",
        json=payload,
        headers={"Authorization": f"Bearer {FLW_SECRET_KEY}"}

    )

    data = r.json()

    if not data.get("status") == "success":
        raise HTTPException(400, "Payment initialization failed")

    return {"payment_link": data["data"]["link"]}

@app.get("/admission/verify")
def admission_verify(
    tx_ref: str,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"

    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {os.getenv('FLW_SECRET_KEY')}"}
    )
    data = r.json()

    if data["status"] != "success":
        raise HTTPException(400, "Verification failed")

    meta = data["data"]["meta"]

    # Generate tracking code
    year = datetime.now().year
    count = db.query(AdmissionApplication).count() + 1
    tracking = f"ADM-{year}-{count:06d}"

    app = AdmissionApplication(
        full_name=meta["full_name"],
        email=meta["email"],
        phone=meta["phone"],
        payment_ref=tx_ref,
        payment_amount=meta["application_fee"],
        tracking_code=tracking,
        status="PAID"
    )

    db.add(app)
    db.commit()
    db.refresh(app)

    return {
        "message": "Payment verified",
        "tracking_code": tracking
    }

@app.post("/admission/submit")
def admission_submit(
    tracking_code: str = Form(...),
    faculty: str = Form(...),
    course: str = Form(...),
    admission_type: str = Form(...),
    gender: str = Form(...),
    dob: str = Form(...),

    nin_file: UploadFile = File(...),
    birth_cert_file: UploadFile = File(...),
    olevel_file: UploadFile = File(...),
    passport_file: UploadFile = File(...),
    transcript_file: UploadFile = File(None),

    db: Session = Depends(get_db)
):
    app_rec = db.query(AdmissionApplication).filter_by(tracking_code=tracking_code).first()

    if not app_rec:
        raise HTTPException(404, "Invalid tracking code")

    if app_rec.status != "PAID":
        raise HTTPException(400, "Application form locked until payment is confirmed")

    def save_file(upload: UploadFile, subfolder: str):
        ext = upload.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        path = os.path.join(ADMISSION_DIR, subfolder, filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(upload.file, f)
        return f"uploads/admission/{subfolder}/{filename}"

    app_rec.nin_file = save_file(nin_file, "nin")
    app_rec.birth_cert_file = save_file(birth_cert_file, "birth")
    app_rec.olevel_file = save_file(olevel_file, "olevel")
    app_rec.passport_file = save_file(passport_file, "passport")

    if transcript_file:
        app_rec.transcript_file = save_file(transcript_file, "transcript")

    app_rec.faculty = faculty
    app_rec.course = course
    app_rec.admission_type = admission_type
    app_rec.gender = gender
    app_rec.dob = dob

    app_rec.status = "SCREENING"
    db.commit()

    return { "message": "OK", "tracking_code": app_rec.tracking_code }

@app.get("/admin/admission/list")
def admin_admission_list(
    status: str | None = None,
    search: str | None = None,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    q = db.query(AdmissionApplication)

    if status:
        q = q.filter(AdmissionApplication.status == status)

    if search:
        pattern = f"%{search}%"
        q = q.filter(
            AdmissionApplication.full_name.ilike(pattern) |
            AdmissionApplication.phone.ilike(pattern) |
            AdmissionApplication.tracking_code.ilike(pattern)
        )

    q = q.order_by(AdmissionApplication.created_at.desc()).all()

    return [
        {
            "id": a.id,
            "name": a.full_name,
            "phone": a.phone,
            "tracking": a.tracking_code,
            "status": a.status,
            "created": a.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for a in q
    ]

@app.get("/admin/admission/view/{app_id}")
def admin_view_admission(
    app_id: int,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    app = db.query(AdmissionApplication).get(app_id)

    if not app:
        raise HTTPException(404, "Application not found")

    return {
        "id": app.id,
        "name": app.full_name,
        "email": app.email,
        "phone": app.phone,
        "gender": app.gender,
        "dob": app.dob,
        "faculty": app.faculty,
        "course": app.course,
        "type": app.admission_type,
        "tracking": app.tracking_code,
        "status": app.status,

        "documents": {
            "passport": app.passport_file,
            "nin": app.nin_file,
            "birth": app.birth_cert_file,
            "olevel": app.olevel_file,
            "transcript": app.transcript_file
        },

        "created": app.created_at.strftime("%Y-%m-%d %H:%M")
    }
@app.post("/admin/admission/status")
def admin_update_admission_status(
    app_id: int = Form(...),
    status: str = Form(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    valid = ["SCREENING", "ACCEPTED", "REJECTED", "ADMITTED"]

    if status not in valid:
        raise HTTPException(400, "Invalid status")

    app = db.query(AdmissionApplication).get(app_id)
    if not app:
        raise HTTPException(404, "Application not found")

    app.status = status
    db.commit()

    return {
        "message": "Status updated",
        "status": status,
        "tracking_code": app.tracking_code
    }
@app.get("/admission/track")
def track(tracking: str, db: Session = Depends(get_db)):
    app_rec = db.query(AdmissionApplication).filter_by(tracking_code=tracking).first()
    if not app_rec:
        raise HTTPException(404, "Tracking code not found")
    return {
        "name": app_rec.full_name,
        "faculty": app_rec.faculty,
        "course": app_rec.course,
        "type": app_rec.admission_type,
        "status": app_rec.status,
        "letter": app_rec.offer_letter_url
    }

@app.post("/admin/admission/letter")
def admin_upload_letter(
    app_id: int = Form(...),
    file: UploadFile = File(...),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    app_rec = db.query(AdmissionApplication).get(app_id)
    if not app_rec:
        raise HTTPException(404, "Application not found")

    # allow letter upload once ACCEPTED or during ADMIT action
    if app_rec.status not in ["ACCEPTED", "ADMITTED"]:
        raise HTTPException(400, "Applicant must be ACCEPTED or ADMITTED before sending letter")

    # PDF validation
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF admission letters are allowed")

    # save file
    folder = "uploads/admission/letters"
    os.makedirs(folder, exist_ok=True)

    filename = f"{uuid.uuid4()}.pdf"
    path = f"{folder}/{filename}"

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    app_rec.offer_letter_url = "/" + path
    app_rec.offer_letter_sent_at = datetime.utcnow()

    # automatically admit student after letter upload
    app_rec.status = "ADMITTED"

    db.commit()
    db.refresh(app_rec)

    return {
        "message": "OK",
        "tracking_code": app_rec.tracking_code,
        "letter": app_rec.offer_letter_url
    }

@app.get("/public/faculties")
def get_public_faculties():
    return list(FACULTY_COURSES.keys())

@app.get("/public/courses")
def get_public_courses(faculty: str):
    clean = faculty.strip().upper()

    for fac in COURSES_BY_FACULTY:
        if fac.upper() == clean:
            return list(COURSES_BY_FACULTY[fac].keys())

    # fallback fuzzy match
    for fac in COURSES_BY_FACULTY:
        if clean in fac.upper():
            return list(COURSES_BY_FACULTY[fac].keys())

    return []


@app.post("/student/courseform/init")
def course_form_flutterwave_init(
    student=Depends(require_student),
    db: Session = Depends(get_db)
):
    semester = get_current_semester(db)

    existing = db.query(CourseFormPayment).filter_by(
        student_id=student.id,
        semester=semester,
        paid=True
    ).first()

    if existing:
        return {"paid": True, "message": "Already paid"}

    # Create pending entry
    cf = CourseFormPayment(
        student_id=student.id,
        semester=semester,
        amount=5000,
        paid=False
    )
    db.add(cf)
    db.commit()

    url = "https://api.flutterwave.com/v3/payments"

    payload = {
        "tx_ref": f"COURSEFORM-{cf.id}",
        "amount": 5000,
        "currency": "NGN",
        "redirect_url": "http://127.0.0.1:8000/api/student/courseform/verify",
        "customer": {
            "email": student.email,
            "name": student.full_name,
        },
        "meta": {
            "student_id": student.id,
            "course_form_id": cf.id,
            "semester": semester
        }
    }

    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(url, json=payload, headers=headers)
    data = r.json()

    if data.get("status") != "success":
        print("FLUTTERWAVE COURSEFORM ERROR:", data)
        raise HTTPException(400, "Flutterwave course form initialization failed")

    return {
        "authorization_url": data["data"]["link"]
    }

@app.get("/student/courseform/verify")
def course_form_flutterwave_verify(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}"
    }

    r = requests.get(url, headers=headers)
    data = r.json()

    if data.get("status") != "success":
        return RedirectResponse("/static/student-dashboard.html?course_failed=1")

    trx = data["data"]

    if trx["status"] != "successful":
        return RedirectResponse("/static/student-dashboard.html?course_failed=1")

    meta = trx["meta"]
    cf_id = meta["course_form_id"]
    student_id = meta["student_id"]

    cf = db.query(CourseFormPayment).filter_by(
        id=cf_id,
        student_id=student_id
    ).first()

    if not cf:
        return RedirectResponse("/static/student-dashboard.html?course_failed=1")

    # Mark paid
    cf.paid = True
    db.commit()

    return RedirectResponse("/static/student-dashboard.html?course_paid=1")


from fastapi import UploadFile, File, Depends
from fastapi.responses import JSONResponse
import uuid, os

UPLOAD_DIR = "uploads/lesson_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/admin/upload-lesson-image")
async def upload_lesson_image(
    image: UploadFile = File(...),
    admin: User = Depends(admin_required)
):
    ext = image.filename.split(".")[-1].lower()
    if ext not in ["png", "jpg", "jpeg", "gif", "webp"]:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid image type"}
        )

    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(await image.read())

    return {
        "url": f"/uploads/lesson_images/{filename}"
    }










