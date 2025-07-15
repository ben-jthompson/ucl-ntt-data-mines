from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/home', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello'})

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    upload_folder = os.path.join(os.getcwd(), "uploads")

    # Ensure the upload directory exists
    try:
        os.makedirs(upload_folder, exist_ok=True)
    except OSError as e:
        return jsonify({"error": f"Failed to create upload directory: {e}"}), 500

    filepath = os.path.join(upload_folder, file.filename)

    # Attempt to save the file
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {e}"}), 500

    return jsonify({"success": "File uploaded successfully", "filename": file.filename}), 200


@app.route("/api/delete", methods=["POST"])
def delete_file():
    print("request is", request)
    return jsonify({"success": "File uploaded successfully", "filename": file.filename}), 200


if __name__ == '__main__':
    app.run(debug=True, port=8080)

