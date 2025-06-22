from flask import Flask, render_template, request, jsonify
from audio import run

app = Flask(__name__)


@app.route('/link', methods=['POST'])
def index():
    link = request.get_json().get('link')
    if not link:
        return jsonify({'error': 'No link provided'}), 400

    run(link)


if __name__ == '__main__':
    app.run()

