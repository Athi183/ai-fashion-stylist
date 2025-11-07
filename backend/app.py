# backend/app.py
import os
from segmentation import remove_background

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from groq import Groq
# backend/app.py
import os
from dotenv import load_dotenv
load_dotenv()  # ✅ Load .env BEFORE using env vars

from groq import Groq 
import replicate
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {"png", "jpg", "jpeg"}

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No image part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

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

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    theme = data.get("theme", "casual")
    body_type = data.get("body_type", "average")
    gender = data.get("gender", "unisex")

    prompt = f"""
You are an expert fashion stylist. Suggest 3 outfit combinations for a {gender} person 
with a {body_type} body type, in {theme} style.
Each suggestion must include:
- Top
- Bottom
- Shoes
- Accessories
- One sentence vibe description
Keep wording simple and practical.
"""

    response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a fashion assistant."},
        {"role": "user", "content": prompt}
    ]
)
    text = response.choices[0].message.content
    return jsonify({"recommendations": text})
import replicate

@app.route("/generate_outfit", methods=["POST"])
def generate_outfit():
    data = request.get_json()
    filename = data["filename"]
    theme = data["theme"]

    person_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{filename}_person.png")

    prompt = f"A {theme} outfit, realistic fabric textures & lighting, preserve face, preserve body, high-quality result"

    output = replicate.run(
        "omnious/vella-1.5",
        input={
            "person_image": open(person_path, "rb"),
            "prompt": prompt,
            "num_inference_steps": 35,
            "guidance_scale": 7.5
        }
    )

    # Some models return list, some dict: inspect output
    # For example:
    result_url = output["output"][0] if isinstance(output, dict) else output[0]

    return jsonify({"generated_url": result_url})
if __name__ == "__main__":
    app.run(port=5000, debug=True)
