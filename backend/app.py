# creating the flast app

from flask import Flask
from config import Config
from extensions import db, migrate
from flask_cors import CORS



def create_app():

    app = Flask(__name__)


    CORS(app, resources={r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Headers"],
        "supports_credentials": True
    }})


    app.config.from_object(Config)

    db.init_app(app)

    migrate.init_app(app, db)

    
    from models import (
        RemoteLab, 
        ROIConfig, 
        StreamLog, 
        RLDecisionLog
    )


    from routes.roi import roi_bp
    from routes.dash import dash_bp
    from routes.lab import lab_bp

    app.register_blueprint(roi_bp, url_prefix="/api")
    app.register_blueprint(dash_bp, url_prefix="/api")
    app.register_blueprint(lab_bp, url_prefix="/api")




    return app

app = create_app()

if __name__ == "__main__":
    ##app.run(debug=True)
    # Add host='0.0.0.0' to allow network IP access
    app.run(host='0.0.0.0', port=5000, debug=True)
