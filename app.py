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
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "a_default_secret_key"

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


# @app.route("/login")
# def login():
#    return render_template("login.html")


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


@app.route("/user_registration", methods=["GET", "POST"])
def user_registration():
    chosen_course = request.args.get("course", "")
    if request.method == "POST":
        pass
    return render_template("user_registration.html", course=chosen_course)


@app.route("/submit_registration", methods=["POST"])
def submit_registration():
    name = request.form["name"]
    birthday = request.form["birthday"]
    email1 = request.form["email1"]
    email2 = request.form["email2"]
    password = request.form["password"]
    chosen_course = request.form["course"]

    # メールアドレスの不一致
    if email1 != email2:
        flash("メールアドレスが一致しません")
        return redirect(url_for("user_registration", course=chosen_course))
    # メールアドレスが一致→ユーザー情報をデータベースに保存
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    new_user = User(
        name=name,
        birthday=birthday,
        email=email1,
        password_hashed=hashed_password,
        course=chosen_course,
        register_time=datetime.datetime.now(),
    )
    new_user.save()

    return render_template(
        "thank_you_registration.html",
        name=name,
        birthday=birthday,
        email=email1,
        password_len=len(password),
        course=chosen_course,
    )


# @app.route("/login", methods=["GET", "POST"])
# def login():
#    if request.method == "POST":
#        email = request.form["email"]
#        password = request.form["password"]
#
#        user = User.select().where(User.email == email).first()

#        # メールアドレスがデータベースにない場合
#        if not user:
#            flash("メールアドレスが登録されていません")
#            return redirect(url_for("login"))

#        # パスワードが一致しない場合
#        if not check_password_hash(user.password_hashed, password):
#            flash("メールアドレスとパスワードが一致しません")
#            return redirect(url_for("login"))
#
#        return redirect(url_for("menu"))
#
#    return render_template("login.html")
#


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.select().where(User.email == email).first()

        # メールアドレスがデータベースにない場合
        if not user:
            flash("メールアドレスが登録されていません もう一度入力してください")
            return redirect(url_for("login"))

        # パスワードが一致しない場合
        if not check_password_hash(user.password_hashed, password):
            flash("メールアドレスとパスワードが一致しません  もう一度入力してくださ")
            return redirect(url_for("login"))

        return redirect(url_for("menu"))

    return render_template("login.html")


@app.route("/menu")
def menu():
    # 12. のステップ
    return render_template("menu.html")


@app.route("/edit_data", methods=["GET", "POST"])
def edit_data():
    # 13. のステップ
    if request.method == "POST":
        # ここで入力データの更新をデータベースに保存する処理
        return redirect(url_for("confirm_data"))

    courses = ["Course 1", "Course 2", "Course 3", "Course 4", "Course 5"]
    return render_template("edit_data.html", courses=courses)


@app.route("/confirm_data")
def confirm_data():
    # 14. のステップ
    return render_template("confirm_data.html")


@app.route("/thank_you_edit", methods=["POST"])
def thank_you_edit():
    # 15. と 16. のステップ
    if request.form.get("confirm") == "no":
        return redirect(url_for("edit_data"))
    elif request.form.get("confirm") == "yes":
        # ここで変更をデータベースに保存
        return render_template("thank_you_edit.html")


# ...（その他のルートと関数）

if __name__ == "__main__":
    app.run(debug=True, port=8000)
