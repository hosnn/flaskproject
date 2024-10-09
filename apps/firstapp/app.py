from flask import Flask, render_template, url_for, request, redirect, flash
from email_validator import validate_email, EmailNotValidError
import logging
from flask_debugtoolbar import DebugToolbarExtension
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# 비밀키 추가
app.config['SECRET_KEY'] = '1234'

# 로그 레벨 설정
app.logger.setLevel(logging.DEBUG)

# 로그 출력 방법
# app.logger.critical('critical')
# app.logger.error('error')
# app.logger.warning('warning')
# app.logger.info('info')
# app.logger.debug('debug')

# 리다이렉트를 중단하지 않도록 한다
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

# DebugToolbarExtension에 애플리케이션을 세트한다
toolbar = DebugToolbarExtension(app)

# Mail 클래스의 컨피그를 추가한다
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

# flask-mail 확장을 등록한다
mail = Mail(app)

@app.route("/")
def index():
  return "hello flask world!"

@app.route("/hello/<name>")
def hello(name):
  return render_template('index.html', name=name)

@app.route('/contact')
def contact():
  return render_template('contact.html')

@app.route('/contact/complete', methods=['get', 'post'])
def contact_complete():
  if request.method == 'POST':
    username = request.form['username']
    email = request.form['email']
    description = request.form['description']

    is_vali = True

    if not username:
      flash("사용자명은 필수입니다")
      is_vali = False

    if not email:
      flash("메일 주소는 필수입니다")
      is_vali = False

    try:
      validate_email(email)
    except EmailNotValidError:
      flash("메일 주소의 형식으로 입력해 주세요")
      is_vali = False

    if not description:
      flash("문의 내용은 필수입니다")
      is_vali = False

    if not is_vali:
      return redirect(url_for("contact"))

    # 이메일 전송기능 구현
    send_email(
        email,
        "문의 감사합니다.",
        "contact_mail",
        username=username,
        description=description,
    )

    # 이메일 전송이 완료되면 전송완료 페이지로 이동하도록 리다이렉트 함
    flash('빠른시일 내로 답변해드리도록 하겠습니다.')
    return redirect(url_for('contact_complete'))
  
  # 전송 완료 후 리다이렉트하게되면 다시 get요청 받아서 이쪽으로 넘어옴
  return render_template('contact_complete.html')

def send_email(to, subject, template, **kwargs):
    # 메일을 송신하는 함수
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)