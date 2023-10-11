import os
import datetime
import logging
from playhouse.db_url import connect
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from peewee import Model, IntegerField, CharField, TextField, TimestampField, SqliteDatabase


load_dotenv()

app = Flask(__name__)

# dbへの接続
db = connect(os.environ.get("DATABASE"))

if not db.connect():
    print("接続NG")
    exit()


class User(Model):
    id = IntegerField(primary_key=True)  # idは自動で追加されるが明示
    name = CharField()
    birthday = CharField()
    email = CharField(unique=True)
    password_hashed = CharField()
    course = CharField()
    register_time = TimestampField(default=datetime.datetime.now)

    class Meta:
        database = db
        table_name = "Users"


db.create_tables([User])


@app.before_request
def before_request():
    db.connect()


@app.after_request
def after_request(response):
    db.close()
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new")
def new():
    return render_template("second_screen.html")


@app.route("/course_recommendation")
def course_recommendation():
    # RECOMMENDERの第一ページ(仮設)に遷移
    return render_template("recommender_top.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/choose_course")
def choose_course():
    return render_template("choose_course.html")


@app.route("/confirm_course")
def confirm_course():
    chosen_course = request.args.get("course", "")
    return render_template("confirm_course.html", course=chosen_course)


@app.route("/register_course")
def register_course():
    chosen_course = request.args.get("course", "")
    return render_template("register_course.html", course=chosen_course)


@app.route("/thank_you")
def thank_you():
    return render_template("thank_you.html")


# ...（その他のルートと関数）

if __name__ == "__main__":
    app.run(debug=True, port=8000)
