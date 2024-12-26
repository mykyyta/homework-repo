from flask import Flask, request, jsonify, render_template, redirect, session
from functools import wraps
import sqlite3
from sqlalchemy import select, outerjoin, join, and_, or_
from database import init_db, db_session
import models
import tasks


app = Flask(__name__)
init_db()
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


class DataBaseCon:
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
    def select(table_name, filter_dict = None, join_dict = None, join = 'JOIN'):
        if filter_dict is None:
            filter_dict = {}
        if join_dict is None:
            join_dict = {}

        with DataBaseCon('db1.sqlite') as db1_cur:
            query = f'SELECT * FROM {table_name}'

            for join_table, join_info in join_dict.items():
                conditions = []
                for condition in join_info.get('on', []):
                    conditions.append(f'{table_name}.{condition[0]} = {join_table}.{condition[1]}')
                for custom_condition in join_info.get('conditions', []):
                    conditions.append(f'{join_table}.{custom_condition[0]} = ?')
                query += f' {join} {join_table} ON ' + ' AND '.join(conditions)

            if filter_dict:
                query += ' WHERE ' + ' AND '.join(f'{key} = ?' for key in filter_dict.keys())

            join_params = [cond[1] for join in join_dict.values() for cond in join.get('conditions', [])]
            filter_params = list(filter_dict.values())

            db1_cur.execute(query, tuple(join_params + filter_params))
            return db1_cur.fetchall()


    @staticmethod
    def insert(table_name, data_dict):
        with (DataBaseCon('db1.sqlite') as db1_cur):
            query = f'''INSERT INTO {table_name} ({' , '.join(data_dict.keys())}) VALUES ({' , '.join([':' + key for key in data_dict.keys()])})'''
            db1_cur.execute(query, data_dict)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

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
        stmt = select(models.User).where(models.User.login == request.form['login'], models.User.password == request.form['password'])
        existing_user = db_session.execute(stmt).scalar()
        #existing_user = DBManager.select('user',{'login' : request.form['login'], 'password': request.form['password']})
        if existing_user:
                session['id'] = existing_user.id
                session['full_name'] = existing_user.full_name
                return redirect('/profile')
        return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    elif request.method == 'POST':
        query_dict = request.form.to_dict()
        user = models.User(**query_dict)
        db_session.add(user)
        db_session.commit()
        #DBManager.insert('user', query_dict)
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
        stmt = select(models.User).where(models.User.id == session['id'])
        user = db_session.execute(stmt).scalar()
        return render_template('profile.html', login=user.login)

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
            join_condition = and_(models.Item.id == models.Favorite.favorite_item, models.Favorite.user == session['id'])
            join_stmt = outerjoin(models.Item, models.Favorite, join_condition)
            stmt = select(models.Item, models.Favorite).select_from(join_stmt).where(models.Item.owner == session['id'])
            selected_items = db_session.execute(stmt).all()
        elif logged_in:
            join_condition = and_(models.Item.id == models.Favorite.favorite_item, models.Favorite.user == session['id'])
            join_stmt = outerjoin(models.Item, models.Favorite, join_condition)
            stmt = select(models.Item, models.Favorite).select_from(join_stmt)
            selected_items = db_session.execute(stmt).all()
        else:
            rows = db_session.execute(select(models.Item)).all()
            selected_items = [(row[0], None) for row in rows]

        return render_template('items.html', items = selected_items, logged_in=logged_in)

    elif request.method == 'POST':
        if not logged_in:
            return redirect('/login')
        new_item_dict = request.form.to_dict()
        new_item_dict['owner'] = session['id']
        new_item = models.Item(**new_item_dict)
        db_session.add(new_item)
        db_session.commit()
        return redirect('/items?my_items=true')


@app.route('/items/<item_id>', methods=['GET'])
@login_check
def item(item_id):
    item_profile = db_session.execute(select(models.Item).where(models.Item.id == item_id)).scalar()

    item_contracts = db_session.execute(
        select(models.Contract).where(models.Contract.item == item_id)
    ).scalars().all()

    unavailable_dates = []
    for one_contract in item_contracts:
        unavailable_dates.append({
            "start_date": one_contract.start_date,
            "end_date": one_contract.end_date
        })

    error_message = request.args.get('error')

    return render_template('item_id.html',item=item_profile, unavailable_dates=unavailable_dates, error=error_message)

@app.route('/items/<item_id>/delete', methods=['POST'])
@login_check
def item_delete(item_id):
    item_profile = db_session.execute(select(models.Item).where(models.Item.id == item_id)).scalar()


    if item_profile:

        item_contracts = db_session.query(models.Contract).filter(models.Contract.item == item_id).all()

        if item_contracts:
            error_message = "Item cannot be deleted because it has active contracts"
            return redirect(f'/items/{item_id}?error={error_message}')

        db_session.delete(item_profile)
        db_session.commit()
        return redirect('/items?my_items=True')
    else: 'item not exists'


@app.route('/profile/favorites', methods=['GET', 'POST'])
@login_check
def favorites():
    if request.method == 'GET':
        join_stmt = join(models.Item, models.Favorite, models.Favorite.favorite_item == models.Item.id)
        where_condition = (models.Favorite.user == session['id'])
        stmt = select(models.Item, models.Favorite).select_from(join_stmt).where(where_condition)
        selected_items = db_session.execute(stmt).all()
        return render_template('favorites.html', items=selected_items)
    else:
        item_id = request.form.get('item_id')
        action = request.form.get('action')
        if action == 'add':
            favorite = models.Favorite(session['id'], item_id)
            db_session.add(favorite)
            db_session.commit()
        elif action == 'delete':
            stmt = select(models.Favorite).where(models.Favorite.favorite_item == item_id,
                                                 models.Favorite.user == session['id'])
            favorite = db_session.execute(stmt).scalar()
            db_session.delete(favorite)
            db_session.commit()
        return redirect(request.referrer)

@app.route('/leasers', methods=['GET'])
@login_check
def leasers():
    leasers_list = db_session.execute(select(models.User)).scalars()
    return render_template('leasers.html', leasers = leasers_list)


@app.route('/leasers/<leaser_id>', methods=['GET'])
@login_check
def leaser(leaser_id):
    user = db_session.execute(select(models.User).where(models.User.id == leaser_id)).scalar()
    return render_template('leaser_id.html', user = user)

@app.route('/contracts', methods=['GET', 'POST'])
@login_check
def contracts():
    if request.method == 'GET':
        leaser_contracts = db_session.execute(select(models.Contract).where(models.Contract.leaser == session['id'])).scalars()
        taker_contracts = db_session.execute(select(models.Contract).where(models.Contract.taker == session['id'])).scalars()
        return render_template('contracts.html',
                               leaser_contracts = leaser_contracts,
                               taker_contracts = taker_contracts)

    elif request.method == 'POST':
        new_contract_dict = request.form.to_dict()
        start_date = new_contract_dict['start_date']
        end_date = new_contract_dict['end_date']
        item_id = new_contract_dict['item']

        conflicting_contracts = db_session.execute(
            select(models.Contract).where(
                models.Contract.item == item_id,
                or_(
                    and_(models.Contract.start_date <= start_date, models.Contract.end_date >= start_date),
                    and_(models.Contract.start_date <= end_date, models.Contract.end_date >= end_date),
                    and_(models.Contract.start_date >= start_date, models.Contract.end_date <= end_date)
                )
            )
        ).scalars().all()

        if conflicting_contracts:
            error_message = "The selected dates are unavailable for this item"
            return redirect(f"/items/{item_id}?error={error_message}")

        new_contract_dict['taker'] = session['id']
        new_contract_dict['text'] = 'contract text'
        new_contract = models.Contract(**new_contract_dict)
        db_session.add(new_contract)
        db_session.commit()

        contract_id = new_contract.id
        tasks.send_email.delay(contract_id)
        return redirect('/contracts')


@app.route('/contracts/<contract_id>', methods=['GET', 'POST', 'PATCH', 'PUT'])
@login_check
def contract(contract_id):
    if request.method == 'GET':
        contract_id = db_session.execute(select(models.Contract).where(models.Contract.id == contract_id)).scalar()
        return render_template('contract_id.html', contract=contract_id)


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
        history = db_session.execute(select(models.SearchHistory).where(models.SearchHistory.user == session['id'])).scalars()
        return [str(row) for row in history]

    elif request.method == 'DELETE':
        return jsonify({'message': 'search history cleared'})


@app.route('/reviews', methods=['GET', 'POST'])
@login_check
def review():
    if request.method == 'GET':
        reviews_of_user = list(db_session.execute(select(models.Feedback).where(models.Feedback.user == session['id'])).scalars())
        grades = [row.grade for row in reviews_of_user]
        average_grade = sum(grades) / len(grades) if grades else '0'
        reviews_by_user = db_session.execute(select(models.Feedback).where(models.Feedback.author == session['id'])).scalars()
        return render_template('reviews.html',
                               reviews_of_user=reviews_of_user,
                               reviews_by_user=reviews_by_user,
                               average_grade=average_grade)

    elif request.method == 'POST':
        contract_id = request.form['contract_id']
        review_text = request.form['review_text']
        grade = request.form['grade']

        new_feedback = models.Feedback(
                            author=session['id'],
                            user=contract.taker if contract.leaser == session['id'] else contract.leaser,
                            text=review_text,
                            grade=grade
                            )

        db_session.add(new_feedback)
        db_session.commit()


@app.route('/compare', methods=['GET', 'PUT', 'PATCH'])
def compare():
    if request.method == 'GET':
        selected_items = db_session.execute(select(models.Item).where(models.Item.id.in_([1, 2]))).scalars()
        return [str(row) for row in selected_items]
    elif request.method in ['PUT', 'PATCH']:
        return jsonify({'message': 'comparison updated'})

@app.route('/add_task', methods=['GET'])
def add_task():
    tasks.add.delay(1, 2)
    return 'task added'

@app.route('/send_email')
def send_email():
    tasks.send_email.delay('111')
    return "Task sent to Celery"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)