import os
import datetime
import logging
from playhouse.db_url import connect
from flask import Flask, render_template, request, redirect, url_for, flash, session
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
    id = IntegerField(primary_key=True)
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
    return render_template("recommender_top.html")


@app.route("/recommend_course", methods=["POST"])
def recommend_course():
    technical_choice = request.form.get("technical")
    business_choice = request.form.get("business")
    duration_choice = request.form.get("duration")

    recommendation_key = f"{technical_choice},{business_choice},{duration_choice}"

    recommendations = {
        "1,1,1": "磐梯コースがお勧めです",
        "1,1,2": "鎌倉コースがお勧めです",
        "1,2,1": "八幡平コースがお勧めです。(ただし、ドローンも学習することになります)",
        "1,2,2": "宇都宮コースがお勧めです",
        "2,1,1": "館山コースがお勧めです",
        "2,1,2": "館山コースをご検討ください。(ただし、1週間集中コースになります)",
        "2,2,1": "館山コースがお勧めです",
        "2,2,2": "館山コースをご検討ください。(ただし、1週間集中コースになります)",
        "3,1,1": "磐梯コースか八幡平コースをご検討ください。(ただし、磐梯コースではドローンを学ぶことができません。八幡平コースの場合はデザイン思考を学ぶことができません)",
        "3,1,2": "申し訳ございません。お勧めのコースがございません。改めて選び直してください。",
        "3,2,1": "八幡平コースがお勧めです",
        "3,2,2": "八幡平コースをご検討ください。ただし、2週間集中コースになります。",
    }

    recommended_course = recommendations.get(recommendation_key, "選択の組み合わせが不正です")

    return render_template("recommended_course.html", course=recommended_course)


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

        if user and check_password_hash(user.password_hashed, password):
            session["user_email"] = email  # ここでメールアドレスをセッションに保存
            return redirect(url_for("menu"))
    return render_template("login.html")



@app.route("/menu")
def menu():
    # 12. のステップ
    return render_template("menu.html")

@app.route("/edit_data", methods=["GET", "POST"])
def edit_data():
    user_email = session.get("user_email")
    if not user_email:
        flash("ログインしてください。")
        return redirect(url_for("login"))

    user = User.select().where(User.email == user_email).first()
    if not user:
        flash("ユーザー情報が見つかりません。")
        return redirect(url_for("menu"))

    if request.method == "POST":
        # POSTで送信された情報を取得
        new_name = request.form.get("name")
        new_birthday = request.form.get("birthday")
        new_email = request.form.get("email")
        new_course = request.form.get("course")

        # データベースの情報を更新
        user.name = new_name
        user.birthday = new_birthday
        user.email = new_email
        user.course = new_course
        user.save()

        flash("ユーザー情報を更新しました。")
        
        return redirect(url_for("thank_you_edit"))
    else:
        courses = ["鎌倉コース", "宇都宮コース", "館山コース", "磐梯コース", "八幡平コース"]
        return render_template("edit_data.html", courses=courses, name=user.name, birthday=user.birthday, email=user.email, current_course=user.course)

@app.route("/reselect_course", methods=["GET", "POST"])
def reselect_course():
    if request.method == "POST":
        # コースデータの更新をデータベースに保存する処理
        return redirect(url_for("confirm_course2"))

    courses = ["鎌倉コース", "宇都宮コース", "館山コース", "磐梯コース", "八幡平コース"]
    return render_template("reselect_course.html", courses=courses)


@app.route("/confirm_course2")
def confirm_course2():
    chosen_course = request.args.get("course", "")
    return render_template("confirm_course2.html", course=chosen_course)


@app.route("/register_course2")
def register_course2():
    chosen_course = request.args.get("course", "")
    return render_template("update_finished.html", course=chosen_course)


@app.route("/cancel_course", methods=["GET", "POST"])
def cancel_course():
    if request.method == "POST":
        decision = request.form.get("confirm")
        if decision == "yes":
            return redirect(url_for("confirm_cancel"))
        else:
            return redirect(url_for("menu"))
    return render_template("cancel_course.html")


@app.route("/confirm_cancel", methods=["GET", "POST"])
def confirm_cancel():
    return render_template("confirm_cancel.html")


@app.route("/handle_confirm_cancel", methods=["POST"])
def handle_confirm_cancel():
    decision = request.form.get("confirm")
    if decision == "yes":
        return redirect(url_for("thank_you_cancel"))
    else:
        return redirect(url_for("menu"))


@app.route("/thank_you_cancel")
def thank_you_cancel():
    return render_template("thank_you_cancel.html")


@app.route("/confirm_data")
def confirm_data():
    # 14. のステップ
    return render_template("confirm_data.html")


@app.route("/thank_you_edit", methods=["GET"])
def thank_you_edit():
    # 15. と 16. のステップ
    # if request.form.get("confirm") == "no":
    #     return redirect(url_for("edit_data"))
    # elif request.form.get("confirm") == "yes":
        # ここで変更をデータベースに保存
        return render_template("thank_you_edit.html")

@app.route("/logout")
def logout():
    session.pop("user_email", None)  # セッションからメールアドレスを削除
    return redirect(url_for("index"))

# ...（その他のルートと関数）

if __name__ == "__main__":
    app.run(debug=True, port=8000)
