from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    try:
        num1 = float(data['num1'])
        num2 = float(data['num2'])
        result = num1 + num2
        return jsonify({"result": result}), 200
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid input. Please provide numeric values for 'num1' and 'num2'."}), 400

@app.route('/subtract', methods=['POST'])
def subtract():
    data = request.get_json()
    try:
        num1 = float(data['num1'])
        num2 = float(data['num2'])
        result = num1 - num2
        return jsonify({"result": result}), 200
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid input. Please provide numeric values for 'num1' and 'num2'."}), 400

@app.route('/multiply', methods=['POST'])
def multiply():
    data = request.get_json()
    try:
        num1 = float(data['num1'])
        num2 = float(data['num2'])
        result = num1 * num2
        return jsonify({"result": result}), 200
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid input. Please provide numeric values for 'num1' and 'num2'."}), 400

@app.route('/divide', methods=['POST'])
def divide():
    data = request.get_json()
    try:
        num1 = float(data['num1'])
        num2 = float(data['num2'])
        if num2 == 0:
            return jsonify({"error": "Division by zero is not allowed."}), 400
        result = num1 / num2
        return jsonify({"result": result}), 200
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid input. Please provide numeric values for 'num1' and 'num2'."}), 400

if __name__ == '__main__':
    app.run(debug=True)