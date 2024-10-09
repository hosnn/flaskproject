from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager

import os
from apps.config import config

config_key = os.environ.get("FLASK_CONFIG_KEY")

# sqlalchemy 객체 생성
db = SQLAlchemy()
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.login_view = "auth.signup"
login_manager.login_message = "로그인 후 사용 가능"

def create_app():
  app = Flask(__name__)

  # config_key에 해당하는 config 클래스를 읽어온다
  app.config.from_object(config[config_key])

  csrf.init_app(app)

  # SQLAlchemy와 flask 앱을 연결
  db.init_app(app)

  # migrate와 앱, db 연결
  Migrate(app, db)

  login_manager.init_app(app)

  from apps.crud import views as crud_views
  from apps.auth import views as auth_views
  from apps.detector import views as dt_views

  app.register_blueprint(crud_views.crud, url_prefix="/crud")
  app.register_blueprint(auth_views.auth, url_prefix="/auth")
  app.register_blueprint(dt_views.dt)

  app.register_error_handler(404, page_not_found)
  app.register_error_handler(500, internal_server_error)

  return app

def page_not_found(e):
  return render_template("404.html"), 404

def internal_server_error(e):
  return render_template("500.html"), 500