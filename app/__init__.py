from flask import Flask
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

    from .routes.auth import auth
    from .routes.products import products

    app.register_blueprint(auth)
    app.register_blueprint(products)

    @app.route("/")
    def home():
        return """
        <h1>Welcome to My Ecommerce App</h1>
        <p>This app includes user authentication and product management.</p>
        <p><strong>New feature added:</strong> low-stock product status.</p>
        <p>To view product data, go to <a href="/products">/products</a>.</p>
        """

    with app.app_context():
        db.create_all()

    return app