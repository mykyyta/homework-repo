from flask import Flask, request, jsonify, render_template, redirect, session, flash
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = 'ee8780947d4f835ebf18dae4c33136a44c49171d2e781d58f886da1ffd339ff5' # python -c 'import secrets; print(secrets.token_hex())'

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def login_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('id') is None:
            flash('You need to login first!')
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper


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
    if session.get('id') is None:
        return redirect('/login')
    return redirect('/profile')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html') #jsonify({'message': 'login page'})


    elif request.method == 'POST':
        with DataBase('db1.sqlite')  as db1_cur:
            db1_cur.execute("SELECT * FROM user WHERE login=? and password=?", (request.form['login'], request.form['password']))
            existing_user = db1_cur.fetchone()
            if existing_user:
                session['id'] = existing_user['id']
                session['full_name'] = existing_user['full_name']
            else:
                redirect('/login')

            return redirect('/profile')

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
@login_check
def logout():
    session.clear() #session.pop('id', None)
    return redirect('/login')


@app.route('/profile', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@login_check
def profile():
    if session.get('id') is None:
        return redirect('/login')

    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute("SELECT login FROM user WHERE id=?", (session['id'],))
            user = db1_cur.fetchone()
            return render_template('profile.html', login=user['login'])

    elif request.method in ['PUT', 'PATCH']:
        return jsonify({'message': 'Profile updated'})
    elif request.method == 'DELETE':
        return jsonify({'message': 'Profile deleted'})


@app.route('/items', methods=['GET', 'POST'])
def items():
    logged_in = session.get('id') is not None

    if request.method == 'GET':
        my_items = request.args.get('my_items')

        with DataBase('db1.sqlite') as db1_cur:
            if my_items:
                db1_cur.execute("SELECT i.*, f.user is not null AS in_favorites FROM item i LEFT JOIN favorite f ON i.id = f.favorite_item AND f.user=? WHERE i.owner=?", (session['id'], session['id'] ))
                return render_template('items.html', items=db1_cur.fetchall(), logged_in=logged_in)
            db1_cur.execute("SELECT *, f.user is not null AS in_favorites FROM item i LEFT JOIN favorite f ON i.id = f.favorite_item AND f.user=?", (session['id'],))
            return render_template('items.html', items=db1_cur.fetchall(), logged_in=logged_in)

    elif request.method == 'POST':
        if not logged_in:
            return redirect('/login')
        query_dict = request.form.to_dict()
        query_dict['owner'] = session['id']
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('''INSERT INTO item 
                            (name, description, owner, price_hour, price_day, price_week, price_month)
                            VALUES (:name, :description, :owner, :price_hour, :price_day, :price_week, :price_month)''',
                            query_dict)
            return redirect('/items?my_items=true')



@app.route('/items/<item_id>', methods=['GET', 'DELETE'])
def item(item_id):
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM item WHERE id = ?', (item_id,))
            return render_template('item_id.html', item=db1_cur.fetchone())

    elif request.method == 'DELETE':
        return jsonify({'message': f'item {item_id} deleted'})


@app.route('/profile/favorites', methods=['GET', 'POST', 'DELETE', 'PATCH'])
@login_check
def favorites():
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM item i JOIN main.favorite f on i.id = f.favorite_item Where f.user = ?', (session['id'],))
            return render_template('favorites.html', items = db1_cur.fetchall())

    elif request.method == 'POST':
        return jsonify({'message': 'favorite added'})
    elif request.method == 'DELETE':
        return jsonify({'message': 'favorites deleted'})
    elif request.method == 'PATCH':
        return jsonify({'message': 'favorite updated'})


@app.route('/profile/favorites/<favorite_id>', methods=['GET', 'POST', 'DELETE'])
@login_check
def favorite_item(favorite_id):
    if request.method == 'GET':
        return jsonify({'message': f'favorite item {favorite_id}'})
    elif request.method == 'POST':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute(''' INSERT INTO favorite (user, favorite_item) VALUES (?, ?)''', (session['id'], favorite_id))
            return redirect('/items')
    elif request.method == 'DELETE':
        return jsonify({'message': f'favorite {favorite_id} deleted'})


@app.route('/leasers', methods=['GET'])
@login_check
def leasers():
    with DataBase('db1.sqlite') as db1_cur:
        db1_cur.execute('SELECT id, login, full_name, contacts, photo FROM user')
        return render_template('leasers.html', leasers = db1_cur.fetchall())


@app.route('/leasers/<leaser_id>', methods=['GET'])
@login_check
def leaser(leaser_id):
    with DataBase('db1.sqlite') as db1_cur:
        db1_cur.execute('SELECT id, login, full_name, contacts, photo FROM user WHERE id = ?', (leaser_id,))
        return render_template('leaser_id.html', user = db1_cur.fetchone())


@app.route('/contracts', methods=['GET', 'POST'])
@login_check
def contracts():
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM contract WHERE leaser = ?', (session['id'],))
            leaser_contracts = db1_cur.fetchall()
            db1_cur.execute('SELECT * FROM contract WHERE taker = ?', (session['id'],))
            taker_contracts = db1_cur.fetchall()
            return render_template('contracts.html',
                                    leather_contracts = leaser_contracts,
                                    taker_contracts = taker_contracts)


    elif request.method == 'POST':
        with DataBase('db1.sqlite') as db1_cur:
            query_dict = request.form.to_dict()
            query_dict['taker'] = session['id']
            db1_cur.execute('''INSERT INTO contract (start_date, end_date, leaser, taker, item) 
                                VALUES (:start_date, :end_date, :leaser, :taker, :item)''', query_dict)
            return redirect('/contracts')


@app.route('/contracts/<contract_id>', methods=['GET', 'PATCH', 'PUT'])
@login_check
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
@login_check
def search_history():
    if request.method == 'GET':
        with DataBase('db1.sqlite') as db1_cur:
            db1_cur.execute('SELECT * FROM search_history WHERE user = ?', (session['id'],))
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