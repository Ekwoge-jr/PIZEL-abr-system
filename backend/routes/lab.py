from flask import Blueprint, request, jsonify, current_app
from models import RemoteLab, ROIConfig
from extensions import db
from services.ffmpeg_pipeline import generate_dash_stream
from werkzeug.utils import secure_filename
import os
import json
import threading



lab_bp = Blueprint("lab", __name__)

@lab_bp.route("/labs", methods=["POST"])
def create_lab():
    try:
        # 1. Retrieve the text and file assets from the form data payload
        lab_name = request.form.get("name")
        image_file = request.files.get("image")
        video_file = request.files.get("video")

        if not lab_name or not image_file or not video_file:
            return jsonify({"error": "Missing field data or asset file payload"}), 400

        # 2. Safely secure file names to prevent directory traversal exploits
        img_filename = secure_filename(image_file.filename)
        vid_filename = secure_filename(video_file.filename)

        # 3. Define local destination upload directories inside the application context
        # upload_folder = current_app.config.get("UPLOAD_FOLDER", "static/uploads")

    
        upload_folder = current_app.config.get("UPLOAD_FOLDER", os.path.join(current_app.root_path, "media"))

        os.makedirs(upload_folder, exist_ok=True)

        img_path = os.path.join(upload_folder, img_filename)
        vid_path = os.path.join(upload_folder, vid_filename)

        # 4. Write data buffers to server storage space
        image_file.save(img_path)
        video_file.save(vid_path)

        # 5. Insert new RemoteLab entity record. The database generates the incrementing Primary Key ID here.
        new_lab = RemoteLab(
            name=lab_name,
            image_url=img_path,   # Storing target path location references
            video_url=vid_path
        )
        db.session.add(new_lab)
        db.session.commit()

        # Optional: Hand off the video file to your pipeline background process to begin parsing the base segments
        # generate_dash_stream(vid_path, new_lab.id)

        # 6. Hand off the auto-incremented record ID back to your instructor UI form
        return jsonify({
            "message": "Remote laboratory pipeline initialized successfully",
            "lab_id": new_lab.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to initialize lab context entry: {str(e)}"}), 500
    





# A simple global dictionary to keep track of active pipeline statuses in memory
pipeline_status = {}


@lab_bp.route("/labs/complete-pipeline", methods=["POST"])
def complete_pipeline():
    try:
        lab_name = request.form.get("name")
        image_file = request.files.get("image")
        video_file = request.files.get("video") # Intercepted via unified wrapper multi-part stream
        rois_json = request.form.get("rois")

        if not lab_name or not image_file:
            return jsonify({"error": "Missing unified payload parameters"}), 400

        # 1. Store Lab Record
        img_filename = secure_filename(image_file.filename)
        # upload_folder = current_app.config.get("UPLOAD_FOLDER", "static/uploads")

        upload_folder = current_app.config.get("UPLOAD_FOLDER", os.path.join(current_app.root_path, "media"))

        os.makedirs(upload_folder, exist_ok=True)
        img_path = os.path.join(upload_folder, img_filename)
        image_file.save(img_path)
       
        vid_filename = secure_filename(video_file.filename)
        vid_path = os.path.join(upload_folder, vid_filename)
        video_file.save(vid_path)

        new_lab = RemoteLab(
            name=lab_name,
            image_url=img_path,
            video_url=vid_path
        )
        db.session.add(new_lab)
        db.session.commit() # Database creates the new key right here

        # 2. Parse and Save the percentage coordinate structures matrix
        parsed_rois = json.loads(rois_json)
        for roi_data in parsed_rois:
            roi = ROIConfig(
                r_lab_id=new_lab.id,
                name=roi_data["name"],
                x=roi_data["x"],
                y=roi_data["y"],
                width=roi_data["width"],
                height=roi_data["height"]
            )
            db.session.add(roi)
        db.session.commit()
        

        # Initialize the tracker state for this lab ID
        pipeline_status[str(new_lab.id)] = {"status": "processing", "error": None}

        flask_app = current_app._get_current_object()
    
        # Define the background worker target function
        def run_ffmpeg_worker(app, path, lab_id):
            with app.app_context():
                try:
                    generate_dash_stream(path, lab_id)
                    pipeline_status[str(lab_id)] = {"status": "completed", "error": None}
                except Exception as ex:
                    pipeline_status[str(lab_id)] = {"status": "failed", "error": str(ex)}

        # Spawn the FFmpeg task on a separate thread and launch it
        threading.Thread(
            target=run_ffmpeg_worker, 
            args=(flask_app, vid_path, new_lab.id)
        ).start()





        # 3. RUN FFmpeg ENCODER (Synchronously blocks until done, maintaining the client spinner)
        # This function processes the stream according to the newly stored ROIs
        # generate_dash_stream(vid_path, new_lab.id)

        return jsonify({
            "status": "success",
            "message": "Lab, coordinates, and DASH stream compiled perfectly.",
            "lab_id": new_lab.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Pipeline failure context: {str(e)}"}), 500
    



    ## Lightweight Status Check Endpoint
@lab_bp.route("/labs/pipeline-status/<int:lab_id>", methods=["GET"])
def get_pipeline_status(lab_id):
    state = pipeline_status.get(str(lab_id), {"status": "unknown", "error": "No tracking record found."})
    return jsonify(state)