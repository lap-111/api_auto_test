"""Mock 商城服务入口

启动方式：python -m mock_server.app
"""
from flask import Flask, jsonify

from .config import Config
from .models import db
from .routes import admin_bp, cart_bp, order_bp, product_bp, user_bp
from .seed import seed_data


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)

    @app.get("/api/health")
    def health():
        """健康检查"""
        return jsonify({"code": 0, "msg": "success", "data": {"status": "ok"}})

    with app.app_context():
        db.create_all()
        seed_data()

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
