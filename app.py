from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, login_manager
from models import User
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.admin import admin_bp
    from routes.chatbot import chatbot_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(analytics_bp)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        return render_template('index.html')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    with app.app_context():
        db.create_all()
        _seed_admin()

    return app

def _seed_admin():
    from models import User
    if not User.query.filter_by(email='admin@loan.com').first():
        admin = User(name='System Admin', email='admin@loan.com', phone='9999999999',
                     address='Admin Office', is_admin=True)
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print("Admin seeded: admin@loan.com / Admin@123")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
