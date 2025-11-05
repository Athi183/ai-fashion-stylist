# backend/app.py
import os
from segmentation import remove_background

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {"png","jpg","jpeg"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
CORS(app)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXT

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error":"No image part"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error":"No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        # Generate mask and person PNG
        mask_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{filename}_mask.png")
        person_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{filename}_person.png")
        remove_background(save_path, mask_path, person_path)

        return jsonify({
            "message": "saved",
            "filename": filename,
            "image_url": f"/uploads/{filename}",
            "mask_url": f"/uploads/{filename}_mask.png",
            "person_url": f"/uploads/{filename}_person.png"
        }), 200


@app.route("/uploads/<path:filename>")
def serve_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
