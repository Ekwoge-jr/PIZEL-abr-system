from flask import Blueprint, request, jsonify
from models import ROIConfig
from extensions import db

from services.roi_manager import roi_analyzer


roi_bp = Blueprint("roi", __name__)


## save roi
@roi_bp.route("/roi", methods=["POST"])
def save_roi():
    
    data = request.json

    # Ensure 'rois' exists
    if "rois" not in data:
        return jsonify({"error": "Missing 'rois' key"}), 400


    ROIConfig.query.filter_by(
        r_lab_id = data.get("r_lab_id")
    ).delete()


    for roi_data in data["rois"]:
        roi = ROIConfig(
            r_lab_id = data.get("r_lab_id"),  # if you expect this at top level
            name = roi_data["name"],
            x = roi_data["x"],
            y = roi_data["y"],
            width = roi_data["width"],
            height = roi_data["height"]
        )
        db.session.add(roi)

    db.session.commit()


    return jsonify({
        "message": "ROI saved successfully"
    })



## retrieve roi
@roi_bp.route("/roi/<int:r_lab_id>")
def get_rois(r_lab_id):

    rois = ROIConfig.query.filter_by(r_lab_id = r_lab_id).all()

    result = []

    for roi in rois:
        result.append({ 
            "id": roi.id,
            "name": roi.name,
            "x": roi.x,
            "y": roi.y,
            "width": roi.width,
            "height": roi.height
        })

    return jsonify(result)






## route to get roi complexity metrics
@roi_bp.route("/roi/metrics", methods=["GET"])
def roi_metrics():
    ## test
    if not roi_analyzer.latest_metrics:
        return jsonify([
            {"name": "Valve", "complexity": 12.5},
            {"name": "Beaker", "complexity": 4.8}
        ])
    ##

    return jsonify(
        roi_analyzer.latest_metrics
    )




