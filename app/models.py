from app.app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    admin = db.Column(db.Integer, default=0)

    # 定义与收藏的关系
    collections = db.relationship('UserCollection', backref='user', lazy='dynamic',
                                    cascade='all, delete-orphan')

    def __repr__(self):
        return 'User: %s, %s, %s, %s' % (self.id, self.name, self.password, str(self.admin))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password,
            'admin': self.admin
        }


class OutdoorProduct(db.Model):
    __tablename__ = 'outdoor_product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.String(10))
    # 已删除top和view_count字段
    photo = db.Column(db.String(1000))
    derive = db.Column(db.String(255))
    sales = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), default='户外装备')

    # 定义与评论的关系
    comments = db.relationship('ProductComment', backref='product', lazy='select')

    def __repr__(self):
        return ('Product: %s, %s, %s, %s, %s, %s'
                % (self.id, self.name, self.price, self.photo, self.derive, self.sales))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'photo': self.photo,
            'derive': self.derive,
            'sales': self.sales,
            'category': self.category
        }


class ProductComment(db.Model):
    __tablename__ = 'product_comment'  # 如果你之前改了表名，保持这个值即可
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('outdoor_product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # 关键修复：给 db.String() 添加长度参数 5000
    comment = db.Column(db.String(5000))  # 5000 足够容纳大部分用户评论，可根据需求调整

    def __repr__(self):
        return ('Comment: %s, %s, %s'
                % (self.product_id, self.comment, self.user_id))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'comment': self.comment
        }


class UserCollection(db.Model):
    __tablename__ = 'user_collection'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('outdoor_product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 定义与商品的关系
    product = db.relationship('OutdoorProduct', backref='collections')

    # 确保同一用户不能重复收藏同一商品
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product'),)

    def __repr__(self):
        return 'UserCollection: user_id=%s, product_id=%s' % (self.user_id, self.product_id)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class UserBrowseHistory(db.Model):
    __tablename__ = 'user_browse_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('outdoor_product.id'), nullable=False)
    browse_time = db.Column(db.DateTime, default=datetime.now)

    # 定义与用户和商品的关系
    user = db.relationship('User', backref='browse_histories')
    product = db.relationship('OutdoorProduct', backref='browse_histories')

    def __repr__(self):
        return 'UserBrowseHistory: user_id=%s, product_id=%s, time=%s' % (
            self.user_id, self.product_id, self.browse_time
        )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'browse_time': self.browse_time.strftime('%Y-%m-%d %H:%M:%S') if self.browse_time else None
        }


class OrderItem(db.Model):
    __tablename__ = 'order_item'
    item_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_pay = db.Column(db.Integer, default=0)
    is_cancel = db.Column(db.Integer, default=0)
    number = db.Column(db.Integer)

    # 定义与用户的关系
    user = db.relationship('User', backref='orders')

    def __repr__(self):
        return ('OrderItem: %s, %s, %s, %s, %s, %s'
                % (self.item_id, self.product_id, self.user_id, self.is_pay, self.is_cancel, self.number))

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'is_pay': self.is_pay,
            'is_cancel': self.is_cancel,
            'number': self.number
        }