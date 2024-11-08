from flask import Flask, request, jsonify, render_template, redirect, session
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


class DBManager:
    @staticmethod
    def select(table_name, filter_dict = None, join = 'JOIN', join_dict = None):
        if filter_dict is None:
            filter_dict = {}
        if join_dict is None:
            join_dict = {}

        with DataBase('db1.sqlite') as db1_cur:
            query = f'SELECT * FROM {table_name}'

            for join_table, join_info in join_dict.items():
                conditions = []
                for condition in join_info.get('on', []):
                    conditions.append(f'{table_name}.{condition[0]} = {join_table}.{condition[1]}')
                for custom_condition in join_info.get('conditions', []):
                    conditions.append(f'{join_table}.{custom_condition[0]} = ?')
                query += f' {join} {join_table} ON ' + ' AND '.join(conditions)

            join_params = [cond[1] for join in join_dict.values() for cond in join.get('conditions', [])]
            filter_params = list(filter_dict.values())

            # for join_table, conditions in join_dict.items():
            #     query += f' {join} {join_table} ON '
            #     query += ' AND '.join(f'{table_name}.{condition[0]} = {join_table}.{condition[1]}' for condition in conditions)

            if filter_dict:
                query += ' WHERE ' + ' AND '.join(f'{key} = ?' for key in filter_dict.keys())

            db1_cur.execute(query, tuple(join_params + filter_params))
            #db1_cur.execute(query, tuple(value for value in filter_dict.values()))
            return db1_cur.fetchall()


    @staticmethod
    def insert(table_name, data_dict):
        with (DataBase('db1.sqlite') as db1_cur):
            query = f'INSERT INTO {table_name} ({' , '.join(data_dict.keys())}) VALUES ({' , '.join([':' + key for key in data_dict.keys()])})'
            db1_cur.execute(query, data_dict)

@app.route('/')
def hello_world():
    if session.get('id') is None:
        return redirect('/login')
    return redirect('/profile')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        existing_user = DBManager.select('user',{'login' : request.form['login'], 'password': request.form['password']})
        if existing_user:
                session['id'] = existing_user[0]['id']
                session['full_name'] = existing_user[0]['full_name']
                return redirect('/profile')
        return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    elif request.method == 'POST':
        query_dict = request.form.to_dict()
        DBManager.insert('user', query_dict)
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
        user = DBManager.select('user', {'id' : session['id']})[0]
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
        if my_items and logged_in:
            selected_items = DBManager.select('item',
                             {'owner': session['id']},
                             "LEFT JOIN",
                             {'favorite':{'on':[('id', 'favorite_item')], 'conditions':[('user', session['id'])]}})
        elif logged_in:
            selected_items = DBManager.select('item',
                             None,
                             "LEFT JOIN",
                             {'favorite':{'on':[('id', 'favorite_item')], 'conditions':[('user', session['id'])]}})
        else:
            selected_items = DBManager.select('item')

        return render_template('items.html', items = selected_items, logged_in=logged_in)

        # with DataBase('db1.sqlite') as db1_cur:
        #     if my_items and logged_in:
        #         db1_cur.execute("""SELECT i.*, f.user FROM item i
        #                                 LEFT JOIN favorite f ON i.id = f.favorite_item AND f.user = ?
        #                                 WHERE i.owner= ?""",
        #                         (session['id'], session['id']))
        #     elif logged_in:
        #         db1_cur.execute("""SELECT i.*, f.user FROM item i
        #                                 LEFT JOIN favorite f ON i.id = f.favorite_item AND f.user=?""",
        #                         (session['id'],))
        #     else:
        #         db1_cur.execute("SELECT * from item")
        #     return render_template('items.html', items=db1_cur.fetchall(), logged_in=logged_in)

    elif request.method == 'POST':
        if not logged_in:
            return redirect('/login')
        query_dict = request.form.to_dict()
        query_dict['owner'] = session['id']
        DBManager.insert('item', query_dict)
        return redirect('/items?my_items=true')



@app.route('/items/<item_id>', methods=['GET', 'DELETE'])
def item(item_id):
    if request.method == 'GET':
        item_profile = DBManager.select('item', {'id' : item_id})[0]
        return render_template('item_id.html', item=item_profile)

    elif request.method == 'DELETE':
        return jsonify({'message': f'item {item_id} deleted'})


@app.route('/profile/favorites', methods=['GET', 'POST', 'DELETE', 'PATCH'])
@login_check
def favorites():
    if request.method == 'GET':
        favorite_items = DBManager.select('item', {'user' : session['id']}, join_dict={'favorite' : {'on': (('id','favorite_item'),)}})
        return render_template('favorites.html', items=favorite_items)

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
        new_entry = {'user': session['id'], 'favorite_item': favorite_id}
        DBManager.insert('favorite', new_entry)
        return redirect(request.referrer)
    elif request.method == 'DELETE':
        return jsonify({'message': f'favorite {favorite_id} deleted'})


@app.route('/leasers', methods=['GET'])
@login_check
def leasers():
    leasers_list = DBManager.select('user')
    return render_template('leasers.html', leasers = leasers_list)


@app.route('/leasers/<leaser_id>', methods=['GET'])
@login_check
def leaser(leaser_id):
    user = DBManager.select('user', {'id': leaser_id})[0]
    return render_template('leaser_id.html', user = user)

@app.route('/contracts', methods=['GET', 'POST'])
@login_check
def contracts():
    if request.method == 'GET':
        leaser_contracts = DBManager.select('contract', {'leaser': session['id']})
        taker_contracts = DBManager.select('contract', {'taker': session['id']})
        return render_template('contracts.html',
                                    leaser_contracts = leaser_contracts,
                                    taker_contracts = taker_contracts)

    elif request.method == 'POST':
        query_dict = request.form.to_dict()
        query_dict['taker'] = session['id']
        DBManager.insert('contract', query_dict)
        return redirect('/contracts')


@app.route('/contracts/<contract_id>', methods=['GET', 'POST', 'PATCH', 'PUT'])
@login_check
def contract(contract_id):

    if request.method == 'GET':
        return DBManager.select('contract', {'id': contract_id})[0]

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
        return DBManager.select('search_history', {'user': session['id']})

    elif request.method == 'DELETE':
        return jsonify({'message': 'search history cleared'})


@app.route('/reviews', methods=['GET', 'POST'])
@login_check
def review():
    if request.method == 'GET':
        reviews_of_user =DBManager.select('feedback', {'user': session['id']})
        grades = [row["grade"] for row in reviews_of_user]
        average_grade = sum(grades) / len(grades) if grades else '0'
        reviews_by_user = DBManager.select('feedback', {'author': session['id']})
        return render_template('reviews.html',
                               reviews_of_user=reviews_of_user,
                               reviews_by_user=reviews_by_user,
                               average_grade=average_grade)

    elif request.method == 'POST':
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