from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import config
import logging

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=['http://localhost:3000'])
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    from app.routes.user_routes import user_bp
    from app.routes.health_routes import health_bp
    from app.routes.twitter_routes import twitter_routes
    from app.utils.download_models import download_models
    download_models()
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(twitter_routes, url_prefix='/api')
    
    return app