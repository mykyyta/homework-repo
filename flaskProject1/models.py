import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, REAL, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True)
    password = Column(String)
    ipn = Column(Integer, unique=True)
    full_name = Column(String)
    contacts = Column(String)
    photo = Column(String)
    email = Column(String)

    # items = relationship('Item', back_populates='owner_relationship')
    # leasers = relationship('Contract', back_populates='leaser_relationship')
    # takers = relationship('Contract', back_populates='taker_relationship')


    def __init__(self, login, password, ipn, full_name, contacts, photo):
        super().__init__()
        self.login = login
        self.password = password
        self.ipn = ipn
        self.full_name = full_name
        self.contacts = contacts
        self.photo = photo



class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    owner = Column(Integer, ForeignKey('user.id'))
    price_hour = Column(REAL)
    price_day = Column(REAL)
    price_week = Column(REAL)
    price_month = Column(REAL)

    # owner_relationship = relationship('User', back_populates='items')
    # contract_items = relationship('Contract', back_populates='item_relationship')

    def __init__(self, name, description, owner, price_hour, price_day, price_week, price_month):
        super().__init__()
        self.name = name
        self.description = description
        self.owner = owner
        self.price_hour = price_hour
        self.price_day = price_day
        self.price_week = price_week
        self.price_month = price_month

    def __repr__(self):
        return (f"<Item(id={self.id}, name='{self.name}', description='{self.description}', "
                f"owner={self.owner}, price_hour={self.price_hour}, price_day={self.price_day}, "
                f"price_week={self.price_week}, price_month={self.price_month})>")

class Contract(Base):
    __tablename__ = 'contract'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(String)
    end_date = Column(String)
    text = Column(String)
    leaser = Column(Integer, ForeignKey('user.id'))
    taker = Column(Integer, ForeignKey('user.id'))
    item = Column(Integer, ForeignKey('item.id'))
    timestamp = Column(DateTime, default=datetime.datetime.now)

    # leaser_relationship = relationship('User', back_populates='leasers')
    # taker_relationship = relationship('User', back_populates='takers')
    # item_relationship = relationship('Item', back_populates='contract_items')

    def __init__(self, start_date, end_date, text, leaser, taker, item):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.text = text
        self.leaser = leaser
        self.taker = taker
        self.item = item

class Favorite(Base):
    __tablename__ = 'favorite'
    fav_id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(Integer, ForeignKey('user.id'))
    favorite_item = Column(Integer, ForeignKey('item.id'))

    def __init__(self, user, favorite_item):
        super().__init__()
        self.user = user
        self.favorite_item = favorite_item

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, autoincrement=True)
    contract = Column(Integer, ForeignKey('contract.id'))
    author = Column(Integer, ForeignKey('user.id'))
    user = Column(Integer, ForeignKey('user.id'))
    text = Column(String)
    grade = Column(Integer)

    def __init__(self, contract, author, user, text, grade):
        super().__init__()
        self.contract = contract
        self.author = author
        self.user = user
        self.text = text
        self.grade = grade

class SearchHistory(Base):
    __tablename__ = 'search_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(Integer, ForeignKey('user.id'))
    search_text = Column(String)
    timestamp = Column(Integer)

    def __init__(self, user, search_text, timestamp):
        super().__init__()
        self.user = user
        self.search_text = search_text
        self.timestamp = timestamp
