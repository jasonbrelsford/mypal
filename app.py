from flask import Flask, request, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
import os
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

# Twilio API credentials
TWILIO_ACCOUNT_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "+1234567890"
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    otp = db.Column(db.String(6), nullable=True)

db.create_all()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form["phone"]
        otp = str(random.randint(100000, 999999))
        
        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone, otp=otp)
            db.session.add(user)
        else:
            user.otp = otp
        db.session.commit()

        # Send OTP via SMS
        client.messages.create(
            body=f"Your verification code is {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )

        return redirect(url_for("verify", phone=phone))
    return render_template("login.html")

@app.route("/verify/<phone>", methods=["GET", "POST"])
def verify(phone):
    if request.method == "POST":
        otp = request.form["otp"]
        user = User.query.filter_by(phone=phone, otp=otp).first()
        if user:
            session["user"] = user.phone
            return "Login Successful!"
        return "Invalid Code!"
    return render_template("verify.html", phone=phone)

if __name__ == "__main__":
    app.run(debug=True)
