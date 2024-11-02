from flask import Flask, request, jsonify, render_template, redirect
import sqlite3

app = Flask(__name__)


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


class DataBase:

    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.conn.row_factory = dict_factory #sqlite3.Row or dict_factory
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html') #jsonify({'message': 'login page'})
    elif request.method == 'POST':
        return jsonify({'message': 'user logged in'})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute("""INSERT INTO user 
                            (login, password, individual_number, full_name, contacts, photo) 
                            VALUES (?, ?, ?, ?, ?, ?)""",
                            (request.form['login'],
                             request.form['password'],
                             request.form['ipn'],
                             request.form['full_name'],
                             request.form['contacts'],
                             request.form['photo']))
        return redirect('/login')


@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
def logout():
    if request.method == 'GET':
        return jsonify({'message': 'logout page'})
    elif request.method in ['POST', 'DELETE']:
        return jsonify({'message': 'user logged out'})


@app.route('/profile', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def profile():
    if request.method == 'GET':
        return render_template('profile.html')
    elif request.method in ['PUT', 'PATCH']:
        return jsonify({'message': 'Profile updated'})
    elif request.method == 'DELETE':
        return jsonify({'message': 'Profile deleted'})


@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM item')
            return render_template('items.html', items=db1_cur.fetchall())
    elif request.method == 'POST':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('''INSERT INTO item 
                            (name, description, owner, price_hour, price_day, price_week, price_month)
                            VALUES (:name, :description, :owner, :price_hour, :price_day, :price_week, :price_month)''',
                            request.form)
        return redirect('/items')



@app.route('/items/<item_id>', methods=['GET', 'DELETE'])
def item(item_id):
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM item WHERE id = ?', (item_id,))
            return render_template('item_id.html', item=db1_cur.fetchone())
    elif request.method == 'DELETE':
        return jsonify({'message': f'item {item_id} deleted'})


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


@app.route('/leasers', methods=['GET'])
def leasers():
    with DataBase('db1.sqlite') as db1_cur:
        db1_cur.execute('SELECT id, login, full_name, contacts, photo FROM user')
        return render_template('leasers.html', leasers = db1_cur.fetchall())


@app.route('/leasers/<leaser_id>', methods=['GET'])
def leaser(leaser_id):
    with DataBase('db1.sqlite') as db1_cur:
        db1_cur.execute('SELECT id, login, full_name, contacts, photo FROM user WHERE id = ?', (leaser_id,))
        return render_template('leaser_id.html', user = db1_cur.fetchone())


@app.route('/contracts', methods=['GET', 'POST'])
def contracts():
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM contract')
            return db1_cur.fetchall()
    elif request.method == 'POST':
        return jsonify({'message': 'contract added'})


@app.route('/contracts/<contract_id>', methods=['GET', 'PATCH', 'PUT'])
def contract(contract_id):
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM contract WHERE id = ?', (contract_id,))
            return db1_cur.fetchone()
    elif request.method in ['PATCH', 'PUT']:
        return jsonify({'message': f'contract {contract_id} updated'})


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return jsonify({'message': 'search results'})
    elif request.method == 'POST':
        return jsonify({'message': 'search submitted'})


@app.route('/profile/search_history', methods=['GET', 'DELETE'])
def search_history():
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM search_history WHERE user = ?', (1,))
            return db1_cur.fetchall()
    elif request.method == 'DELETE':
        return jsonify({'message': 'search history cleared'})


@app.route('/reviews', methods=['GET'])
def review():
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM feedback')
            return db1_cur.fetchall()
    return jsonify({'message': 'Reviews submitted'})


@app.route('/compare', methods=['GET', 'PUT', 'PATCH'])
def compare():
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT name, price_hour FROM item WHERE id = ? OR id = ?', (1, 2))
            return db1_cur.fetchall()
    elif request.method in ['PUT', 'PATCH']:
        return jsonify({'message': 'comparison updated'})


if __name__ == '__main__':
    app.run(debug=True)