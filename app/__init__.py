import logging
import os
import time
from logging.handlers import RotatingFileHandler

from flask import Flask, g, render_template, request
from flask_login import LoginManager

from config import Config
from .models import db, User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    configure_logging(app)
    configure_request_monitoring(app)
    configure_security_headers(app)

    from .routes.auth import auth
    from .routes.products import products
    from .routes.orders import orders

    app.register_blueprint(auth)
    app.register_blueprint(products)
    app.register_blueprint(orders)

    @app.route("/")
    def home():
        return render_template("index.html")

    with app.app_context():
        db.create_all()

    app.logger.info("Application started successfully.")

    return app


def configure_logging(app):
    """Configure application logging."""

    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", "app.log")

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1024 * 1024,
        backupCount=3,
    )

    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )
    file_handler.setLevel(logging.INFO)

    # Add the file handler unless this exact log file is already configured
    log_path_absolute = os.path.abspath(log_path)

    already_configured = any(
        isinstance(handler, RotatingFileHandler)
        and os.path.abspath(handler.baseFilename) == log_path_absolute
        for handler in app.logger.handlers
    )

    if not already_configured:
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)


def configure_request_monitoring(app):
    """Log every request and its duration."""

    @app.before_request
    def before_request():
        g.start_time = time.perf_counter()

    @app.after_request
    def after_request(response):
        elapsed = time.perf_counter() - g.start_time

        app.logger.info(
            "%s %s | %s | %.4fs | %s",
            request.method,
            request.path,
            response.status_code,
            elapsed,
            request.remote_addr,
        )

        return response
    
def configure_security_headers(app):
    """Add basic security headers to every HTTP response."""

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        return response