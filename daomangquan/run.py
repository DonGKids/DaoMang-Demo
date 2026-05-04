from flask import Flask
from app.routes import bp
from app.models import init_database
import config

def create_app():
    app = Flask(__name__, template_folder='app/templates')  # 强制指定模板路径
    app.config.from_object(config.Config)
    init_database()
    app.register_blueprint(bp)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)