from flask import Flask, request, jsonify, send_file
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
    print('filepath is', filepath)
    # Attempt to save the file
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {e}"}), 500

    return jsonify({"success": "File uploaded successfully", "filename": file.filename}), 200



@app.route("/api/delete", methods=["POST"])
def delete_file():
    print('Deleting file...')
    data = request.get_json()
    print(data)
    if not data['file']:
        print('xf')
        return jsonify({"error": "No file part in the request"}), 400
    file = data['file']

    if file == "":
        print('xd')
        return jsonify({"error": "No selected file"}), 400

    upload_folder = os.path.join(os.getcwd(), "uploads")

    filepath = os.path.join(upload_folder, file)

    # Attempt to save the file
    try:
        os.remove(filepath)
    except Exception as e:
        print('xr')
        return jsonify({"error": f"Failed to save file: {e}"}), 500

    return jsonify({"success": "File uploaded successfully", "filename": 'x'}), 200

@app.route('/api/geojson/<filename>')
def get_geojson(filename):
    filepath = os.path.join('../data/geojson', filename)
    try:
        return send_file(filepath, mimetype='application/json')
    except FileNotFoundError:
        return {"error": "File not found"}, 404



if __name__ == '__main__':
    app.run(debug=True, port=8080)

