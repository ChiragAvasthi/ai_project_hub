from flask import Flask

def create_app():
    """Construct the core application."""
    app = Flask(__name__)
    
    # ADD THIS LINE to set a secret key for session management (e.g., flash messages)
    app.config['SECRET_KEY'] = 'a_truly_secret_key_for_your_project'

    with app.app_context():
        # Import and register blueprints
        from .main.routes import main_bp
        from .cloak.routes import cloak_bp
        from .anonymizer.routes import anonymizer_bp
        from .detector.routes import detector_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(cloak_bp, url_prefix='/cloak')
        app.register_blueprint(anonymizer_bp, url_prefix='/anonymizer')
        app.register_blueprint(detector_bp, url_prefix='/detector')

        return app