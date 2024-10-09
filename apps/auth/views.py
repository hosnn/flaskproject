from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_user, logout_user

from apps.app import db
from apps.auth.forms import SignUpForm, LoginForm
from apps.crud.models import User

auth = Blueprint(
  "auth",
  __name__,
  template_folder="templates",
  static_folder="static"
)

@auth.route("/")
def index():
  return render_template("auth/index.html")

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    # SignUpForm을 인스턴스화한다
    form = SignUpForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )

        # 메일 주소 중복 체크를 한다
        if user.is_duplicate_email():
            flash("지정한 이메일 주소는 이미 등록되어 있습니다.")
            return redirect(url_for("auth.signup"))

        # 사용자 정보를 등록한다
        db.session.add(user)
        db.session.commit()

        # 사용자 정보를 세션에 저장한다
        login_user(user)

        # GET 파라미터에 next 키가 존재하고, 값이 없는 경우는 사용자의 일람 페이지로 리다이렉트한다
        next_ = request.args.get("next")
        if next_ is None or not next_.startswith("/"):
            next_ = url_for("detector.index")
        return redirect(next_)

    return render_template("auth/signup.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # username으로부터 사용자를 취득한다
        user = User.query.filter_by(username=form.username.data).first()

        # 사용자가 존재하고 비밀번호가 일치하는 경우는 로그인을 허가한다
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for("detector.index"))

        # 로그인 실패 메시지를 설정한다
        flash("username 또는 비밀번호가 일치하지 않습니다")
    return render_template("auth/login.html", form=form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))