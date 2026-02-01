# Application factory for Wi-Fi File Share
from flask import Flask

from app.config import MAX_CONTENT_LENGTH


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app
