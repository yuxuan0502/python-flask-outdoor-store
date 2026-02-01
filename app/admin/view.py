from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from app.models import User, OutdoorProduct, OrderItem, ProductComment
from app.app import db
from sqlalchemy import desc
from functools import wraps
from app.admin import admin


# 管理员登录检查装饰器
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查session中是否有admin_id
        if not session.get('admin_id'):
            flash("请先以管理员身份登录")
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)

    return decorated_function


# 管理员登录
@admin.route("/login", methods=['GET', 'POST'])
def login():
    # 如果已经登录，跳转到后台首页
    if session.get('admin_id'):
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("用户名和密码不能为空")
            return render_template("admin/login.html")

        # 查找用户
        user = User.query.filter_by(name=username).first()

        # 验证密码和是否为管理员
        if user and user.password == password and user.admin == 1:
            session['admin_id'] = user.id
            flash("管理员登录成功")
            return redirect(url_for('admin.index'))
        else:
            flash("管理员账号或密码错误")

    return render_template("admin/login.html")


# 管理员退出
@admin.route("/logout")
def logout():
    session.pop('admin_id', None)
    session.pop('user_id', None)
    flash("管理员已退出")
    return redirect(url_for('user.login'))


# 管理员首页
@admin.route("/")
@admin_login_required
def index():
    # 获取管理员信息
    admin_user = User.query.get(session.get('admin_id'))

    # 统计数据
    total_users = User.query.count()
    total_products = OutdoorProduct.query.count()
    total_orders = OrderItem.query.filter_by(is_pay=1).count()

    # 最近订单
    recent_orders = OrderItem.query.filter_by(is_pay=1).order_by(desc('item_id')).limit(5).all()

    return render_template(
        "admin/home.html",
        admin=admin_user,
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        recent_orders=recent_orders
    )


# 商品管理
@admin.route("/item")
@admin_login_required
def item_view():
    admin_user = User.query.get(session.get('admin_id'))
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # 获取所有商品
    query = OutdoorProduct.query.order_by(desc('id'))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    return render_template(
        "admin/item.html",
        products=products,
        page=pagination,
        admin=admin_user
    )


# 用户管理
@admin.route("/user")
@admin_login_required
def user_view():
    admin_user = User.query.get(session.get('admin_id'))
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # 获取所有用户
    query = User.query.order_by(desc('id'))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    return render_template(
        "admin/user.html",
        users=users,
        page=pagination,
        admin=admin_user
    )


# 订单管理
@admin.route("/order")
@admin_login_required
def order_view():
    admin_user = User.query.get(session.get('admin_id'))
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # 获取所有订单
    query = OrderItem.query.order_by(desc('item_id'))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items

    # 为每个订单关联商品和用户信息
    order_list = []
    for order in orders:
        product = OutdoorProduct.query.get(order.product_id)
        user = User.query.get(order.user_id)
        order_list.append({
            'order': order,
            'product': product,
            'user': user
        })

    # 获取所有用户（用于模板显示）
    users = User.query.all()

    return render_template(
        "admin/order.html",
        orders=order_list,
        users=users,
        page=pagination,
        admin=admin_user
    )


# 添加商品
@admin.route("/add_product", methods=['GET', 'POST'])
@admin_login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', '').strip()
        derive = request.form.get('derive', '').strip()
        photo = request.form.get('photo', '').strip()
        category = request.form.get('category', '户外装备').strip()

        if not name or not price:
            flash("商品名称和价格不能为空")
            return redirect(url_for('admin.item_view'))

        try:
            # 创建新商品
            new_product = OutdoorProduct(
                name=name,
                price=float(price),
                derive=derive,
                photo=photo,
                sales=0,
                category=category
            )
            db.session.add(new_product)
            db.session.commit()
            flash("商品添加成功")
        except Exception as e:
            db.session.rollback()
            flash(f"添加商品失败: {str(e)}")

        return redirect(url_for('admin.item_view'))

    return render_template("admin/add_product.html")


# 修改商品
@admin.route("/edit_product/<int:product_id>", methods=['GET', 'POST'])
@admin_login_required
def edit_product(product_id):
    product = OutdoorProduct.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form.get('name', product.name).strip()
        product.price = request.form.get('price', product.price).strip()
        product.derive = request.form.get('derive', product.derive).strip()
        product.photo = request.form.get('photo', product.photo).strip()
        product.category = request.form.get('category', product.category).strip()

        try:
            db.session.commit()
            flash("商品修改成功")
        except Exception as e:
            db.session.rollback()
            flash(f"修改商品失败: {str(e)}")

        return redirect(url_for('admin.item_view'))

    return render_template("admin/edit_product.html", product=product)


# 删除商品
@admin.route("/delete_product/<int:product_id>")
@admin_login_required
def delete_product(product_id):
    product = OutdoorProduct.query.get_or_404(product_id)

    try:
        db.session.delete(product)
        db.session.commit()
        flash("商品删除成功")
    except Exception as e:
        db.session.rollback()
        flash(f"删除商品失败: {str(e)}")

    return redirect(url_for('admin.item_view'))


# 获取订单详情（API）
@admin.route("/get_item/<int:item_id>")
def get_item(item_id):
    order_item = OrderItem.query.get_or_404(item_id)
    user = User.query.get(order_item.user_id)
    product = OutdoorProduct.query.get(order_item.product_id)

    return jsonify({
        'item': {
            'item': order_item.to_dict(),
            'user': user.to_dict() if user else None,
            'product': product.to_dict() if product else None
        }
    })


# 搜索视图（API）
@admin.route("/search_view")
def search_view():
    search_term = request.args.get('search', '')
    text_type = request.args.get('text', '')

    if text_type == 'product':
        products = OutdoorProduct.query.filter(
            OutdoorProduct.name.contains(search_term)
        ).all()
        return jsonify({
            'products': [p.to_dict() for p in products]
        })
    elif text_type == 'order':
        # 先按商品名称搜索
        products = OutdoorProduct.query.filter(
            OutdoorProduct.name.contains(search_term)
        ).all()
        product_ids = [p.id for p in products]

        # 按用户名搜索
        users = User.query.filter(User.name.contains(search_term)).all()

        # 获取所有相关订单（按商品或按用户）
        orders = []
        all_users = set()  # 用于收集所有相关用户

        # 按商品搜索的订单
        if product_ids:
            order_items = OrderItem.query.filter(
                OrderItem.product_id.in_(product_ids)
            ).all()
            for order in order_items:
                product = OutdoorProduct.query.get(order.product_id)
                orders.append({
                    'item_id': order.item_id,
                    'product_id': order.product_id,
                    'user_id': order.user_id,
                    'number': order.number,
                    'is_pay': order.is_pay,
                    'product': {
                        'name': product.name if product else '未知商品',
                        'derive': product.derive if product else '',
                        'price': product.price if product else 0
                    }
                })
                all_users.add(order.user_id)

        # 按用户搜索的订单
        for user in users:
            all_users.add(user.id)
            user_orders = OrderItem.query.filter_by(user_id=user.id).all()
            for order in user_orders:
                # 避免重复添加
                if not any(o['item_id'] == order.item_id for o in orders):
                    product = OutdoorProduct.query.get(order.product_id)
                    orders.append({
                        'item_id': order.item_id,
                        'product_id': order.product_id,
                        'user_id': order.user_id,
                        'number': order.number,
                        'is_pay': order.is_pay,
                        'product': {
                            'name': product.name if product else '未知商品',
                            'derive': product.derive if product else '',
                            'price': product.price if product else 0
                        }
                    })

        # 获取所有相关用户信息
        users_list = User.query.filter(User.id.in_(list(all_users))).all()

        return jsonify({
            'orders': orders,
            'users': [u.to_dict() for u in users_list]
        })
    elif text_type == 'user':
        users = User.query.filter(
            User.name.contains(search_term)
        ).all()
        return jsonify({
            'users': [u.to_dict() for u in users]
        })

    return jsonify({})


# 编辑用户
@admin.route("/edit_user/<int:user_id>", methods=['GET', 'POST'])
@admin_login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name = request.form.get('name', user.name).strip()
        admin_value = request.form.get('admin', str(user.admin))

        # 如果提供了新密码，则更新密码
        new_password = request.form.get('password', '').strip()
        if new_password:
            user.password = new_password

        user.admin = int(admin_value)

        try:
            db.session.commit()
            flash("用户修改成功")
        except Exception as e:
            db.session.rollback()
            flash(f"修改用户失败: {str(e)}")

        return redirect(url_for('admin.user_view'))

    return render_template("admin/edit_user.html", user=user)


# 获取商品评论（API）
@admin.route("/get_comments/<int:product_id>")
def get_comments(product_id):
    comments = ProductComment.query.filter_by(product_id=product_id).all()
    comment_list = []

    for comment in comments:
        user = User.query.get(comment.user_id)
        comment_list.append({
            'id': comment.id,
            'comment': comment.comment,
            'username': user.name if user else '未知用户',
            'user_id': comment.user_id
        })

    return jsonify({'comments': comment_list})


# 删除评论（API）
@admin.route("/delete_comment/<int:comment_id>")
@admin_login_required
def delete_comment(comment_id):
    comment = ProductComment.query.get_or_404(comment_id)

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500