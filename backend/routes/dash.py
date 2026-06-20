from flask import Blueprint
from flask import send_from_directory
from pathlib import Path
from extensions import db


dash_bp = Blueprint("dash", __name__)

DASH_DIR = (Path(__file__).parent.parent / "dash_server")

@dash_bp.route("/dash/<path:filename>")
def dash_files(filename):

    print("Serving:", filename)

    return send_from_directory(

        DASH_DIR,

        filename

    )
