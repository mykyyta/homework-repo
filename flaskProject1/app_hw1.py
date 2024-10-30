from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!!!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return jsonify({'message': 'login page'})
    elif request.method == 'POST':
        return jsonify({'message': 'user logged in'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return jsonify({'message': 'registration page'})
    elif request.method == 'POST':
        return jsonify({'message': 'user registered'})

@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
def logout():
    if request.method == 'GET':
        return jsonify({'message': 'logout page'})
    elif request.method in ['POST', 'DELETE']:
        return jsonify({'message': 'user logged out'})

@app.route('/profile', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def profile():
    if request.method == 'GET':
        return jsonify({'message': 'User profile data'})
    elif request.method in ['PUT', 'PATCH']:
        return jsonify({'message': 'Profile updated'})
    elif request.method == 'DELETE':
        return jsonify({'message': 'Profile deleted'})

@app.route('/profile/favorites', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def favorites():
    if request.method == 'GET':
        return jsonify({'message': 'favorites'})
    elif request.method == 'POST':
        return jsonify({'message': 'favorite added'})
    elif request.method == 'DELETE':
        return jsonify({'message': 'favorites deleted'})
    elif request.method == 'PATCH':
        return jsonify({'message': 'favorite updated'})

@app.route('/profile/favorites/<favorite_id>', methods=['GET', 'DELETE'])
def favorite_item(favorite_id):
    if request.method == 'GET':
        return jsonify({'message': f'favorite item {favorite_id}'})
    elif request.method == 'DELETE':
        return jsonify({'message': f'favorite {favorite_id} deleted'})

@app.route('/profile/search_history', methods=['GET', 'DELETE'])
def search_history():
    if request.method == 'GET':
        return jsonify({'message': 'search history'})
    elif request.method == 'DELETE':
        return jsonify({'message': 'search history cleared'})

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        return jsonify({'message': 'items'})
    elif request.method == 'POST':
        return jsonify({'message': 'item added'})

@app.route('/items/<item_id>', methods=['GET', 'DELETE'])
def item_id(item_id):
    if request.method == 'GET':
        return jsonify({'message': f'item {item_id}'})
    elif request.method == 'DELETE':
        return jsonify({'message': f'item {item_id} deleted'})

@app.route('/leasers', methods=['GET'])
def leasers():
    return jsonify({'leasers': 'list of leasers'})

@app.route('/leasers/<leaser_id>', methods=['GET'])
def leaser_id(leaser_id):
    return jsonify({'leaser': f'details of leaser {leaser_id}'})

@app.route('/contracts', methods=['GET', 'POST'])
def contracts():
    if request.method == 'GET':
        return jsonify({'message': 'contract added'})
    elif request.method == 'POST':
        return jsonify({'message': 'contract added'})

@app.route('/contracts/<contract_id>', methods=['GET', 'PATCH', 'PUT'])
def contract_id(contract_id):
    if request.method == 'GET':
        return jsonify({'contract': f'details of contract {contract_id}'})
    elif request.method in ['PATCH', 'PUT']:
        return jsonify({'message': f'contract {contract_id} updated'})

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return jsonify({'message': 'search results'})
    elif request.method == 'POST':
        return jsonify({'message': 'search submitted'})

@app.route('/complain', methods=['POST'])
def complain():
    return jsonify({'message': 'Complaint submitted'})

@app.route('/compare', methods=['GET', 'PUT', 'PATCH'])
def compare():
    if request.method == 'GET':
        return jsonify({'message': 'comparison results'})
    elif request.method in ['PUT', 'PATCH']:
        return jsonify({'message': 'comparison updated'})

if __name__ == '__main__':
    app.run(debug=True)