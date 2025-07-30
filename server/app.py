from flask import Flask, request, jsonify, send_file, Response, stream_with_context
from flask_cors import CORS
import os
import time
from server.graph.pipeline import Pipeline

app = Flask(__name__)
CORS(app)

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

@app.route("/api/run_pipeline")
def run_pipeline():
    location = request.args.get("location")
    query = request.args.get("query")
    pipeline = Pipeline(location, query)

    def generate():
        yield "data: Starting pipeline...\n\n"
        time.sleep(2)
        yield "data: Scraping documents...\n\n"
        time.sleep(2)
        pipeline.scrape()
        yield "data: Embedding documents...\n\n"
        time.sleep(2)
        pipeline.embed()
        yield "data: Querying LLM...\n\n"
        time.sleep(2)
        result = pipeline.query_llm()
        yield f"data: DONE: {result}\n\n"
        time.sleep(10)
        yield "data: Querying LLM...\n\n"
        yield "data: DONE\n\n"

    return Response(stream_with_context(generate()), content_type='text/event-stream')

    


if __name__ == '__main__':
    app.run(debug=True, port=8080)

