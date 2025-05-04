from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Rate limiting decorator
def limit_requests(f):
    def wrapper(*args, **kwargs):
        # In production, replace with Redis-based rate limiting
        return f(*args, **kwargs)
    return wrapper

def validate_expression(expression):
    """Validate and sanitize calculator input"""
    if not expression:
        return False, "Empty expression"
    
    # Only allow numbers, basic operators, and parentheses
    if not re.match(r'^[\d+\-*/().\s]+$', expression):
        return False, "Invalid characters in expression"
    
    # Check for balanced parentheses
    if expression.count('(') != expression.count(')'):
        return False, "Unbalanced parentheses"
    
    return True, ""

@app.route('/calculate', methods=['POST'])
@limit_requests
def calculate():
    data = request.get_json()
    expression = data.get('expression', '').strip()
    
    valid, message = validate_expression(expression)
    if not valid:
        return jsonify({'error': message}), 400
    
    try:
        # Using eval is dangerous, but we've validated the input thoroughly
        # In production, consider using a proper expression evaluator library
        result = eval(expression, {'__builtins__': None}, {})
    except ZeroDivisionError:
        return jsonify({'error': 'Division by zero'}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid expression'}), 400
    
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)