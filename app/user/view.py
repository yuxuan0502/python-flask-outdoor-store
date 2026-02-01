from flask import render_template, session, redirect, url_for, flash, request, jsonify
from app.models import User, OutdoorProduct, ProductComment, OrderItem, UserCollection, UserBrowseHistory
from app.models import db
import random
from sqlalchemy import desc, func
from . import user
# 在文件顶部添加导入
import pyecharts.options as opts
from pyecharts.charts import Bar, Pie, Line, BMap
import datetime



# 生成图表数据的辅助函数
def generate_chart1():
    """生成销量排行榜图表"""
    try:
        # 获取销量前10的商品
        top_products = OutdoorProduct.query.order_by(desc('sales')).limit(10).all()

        if not top_products:
            return None

        # 提取商品名和销量
        product_names = [p.name[:10] + '...' if len(p.name) > 10 else p.name for p in top_products]
        sales_data = [p.sales for p in top_products]

        # 创建柱状图
        bar = (
            Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
            .add_xaxis(product_names)
            .add_yaxis("销量", sales_data)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="热门商品销量排行", subtitle="Top 10"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=45)
                ),
                yaxis_opts=opts.AxisOpts(
                    name="销量",
                    axislabel_opts=opts.LabelOpts(formatter="{value} 件")
                ),
                datazoom_opts=[opts.DataZoomOpts()],
                toolbox_opts=opts.ToolboxOpts(),
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(is_show=True),
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值"),
                    ]
                ),
            )
        )
        return bar.render_embed()
    except Exception as e:
        print(f"生成图表1时出错: {e}")
        return None


def generate_chart3():
    """生成商品统计图表"""
    try:
        # 按品牌统计商品数量
        brands = db.session.query(
            OutdoorProduct.derive,
            func.count(OutdoorProduct.id).label('count')
        ).group_by(OutdoorProduct.derive).all()

        if not brands:
            return None

        # 准备饼图数据
        brand_names = [brand[0] if brand[0] else '其他' for brand in brands]
        brand_counts = [brand[1] for brand in brands]

        # 创建数据对
        data_pair = [list(z) for z in zip(brand_names, brand_counts)]

        pie = (
            Pie(init_opts=opts.InitOpts(width="100%", height="400px"))
            .add(
                series_name="品牌分布",
                data_pair=data_pair,
                radius=["30%", "75%"],
                center=["50%", "50%"],
                rosetype=None,
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="商品品牌分布",
                    pos_left="center"
                ),
                legend_opts=opts.LegendOpts(
                    type_="scroll",
                    pos_left="80%",
                    orient="vertical",
                    item_width=10,
                    item_height=10
                ),
                toolbox_opts=opts.ToolboxOpts(),
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(
                    formatter="{b}: {c} ({d}%)",
                    font_size=12
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="item",
                    formatter="{a} <br/>{b}: {c} ({d}%)"
                ),
            )
        )
        return pie.render_embed()
    except Exception as e:
        print(f"生成图表3时出错: {e}")
        return None


def generate_chart4():
    """生成销售趋势图表"""
    try:
        # 获取最近7天的日期
        dates = [(datetime.date.today() - datetime.timedelta(days=i)).strftime('%m-%d')
                 for i in range(6, -1, -1)]

        # 这里应该从数据库查询实际销售数据
        # 暂时使用模拟数据
        sales_data = [random.randint(50, 200) for _ in range(7)]

        line = (
            Line(init_opts=opts.InitOpts(width="100%", height="400px"))
            .add_xaxis(dates)
            .add_yaxis(
                "销售额",
                sales_data,
                is_smooth=True,
                is_symbol_show=True,
                symbol="circle",
                symbol_size=8,
                linestyle_opts=opts.LineStyleOpts(width=3)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="近7天销售趋势",
                    pos_left="center"
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross"
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    boundary_gap=False,
                    name="日期"
                ),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="销售额（件）",
                    axislabel_opts=opts.LabelOpts(formatter="{value} 件"),
                    splitline_opts=opts.SplitLineOpts(is_show=True)
                ),
                datazoom_opts=[opts.DataZoomOpts()],
                toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "saveAsImage": {},
                        "dataView": {},
                        "magicType": {"type": ["line", "bar"]},
                        "restore": {},
                        "dataZoom": {}
                    }
                ),
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(is_show=True),
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值"),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type="average", name="平均值")]
                ),
            )
        )
        return line.render_embed()
    except Exception as e:
        print(f"生成图表4时出错: {e}")
        return None


# 协同过滤推荐函数（基于收藏+购买+浏览历史）
def recommend_products(user_id, top_n=5):
    """基于用户的收藏、购买和浏览记录进行协同过滤推荐"""
    # 获取用户收藏的商品
    user_collections = UserCollection.query.filter_by(user_id=user_id).all()
    collection_product_ids = [c.product_id for c in user_collections]

    # 获取用户购买的商品
    user_orders = OrderItem.query.filter_by(user_id=user_id, is_pay=1).all()
    purchase_product_ids = [item.product_id for item in user_orders]

    # 获取用户浏览历史（最近30天，按时间倒序取前50个）
    from datetime import timedelta
    thirty_days_ago = datetime.datetime.now() - timedelta(days=30)
    user_browse_histories = UserBrowseHistory.query.filter(
        UserBrowseHistory.user_id == user_id,
        UserBrowseHistory.browse_time >= thirty_days_ago
    ).order_by(desc(UserBrowseHistory.browse_time)).limit(50).all()
    browse_product_ids = [h.product_id for h in user_browse_histories]

    # 合并用户感兴趣的商品（收藏+购买+浏览）
    user_interest_ids = list(set(collection_product_ids + purchase_product_ids + browse_product_ids))

    if not user_interest_ids:
        # 无收藏、购买和浏览记录推荐销量最高的商品
        return OutdoorProduct.query.order_by(desc('sales')).limit(top_n).all()

    # 找到其他用户收藏或购买过相同商品的记录
    # 先找收藏记录
    other_collections = UserCollection.query.filter(
        UserCollection.product_id.in_(user_interest_ids),
        UserCollection.user_id != user_id
    ).all()

    # 再找购买记录
    other_orders = OrderItem.query.filter(
        OrderItem.product_id.in_(user_interest_ids),
        OrderItem.user_id != user_id,
        OrderItem.is_pay == 1
    ).all()

    # 找浏览记录
    other_browses = UserBrowseHistory.query.filter(
        UserBrowseHistory.product_id.in_(user_interest_ids),
        UserBrowseHistory.user_id != user_id,
        UserBrowseHistory.browse_time >= thirty_days_ago
    ).all()

    # 计算商品共现矩阵（基于收藏、购买和浏览）
    # 浏览权重为1，收藏权重为2，购买权重为3（购买行为最能反映偏好）
    product_coocur = {}

    # 处理其他用户的浏览
    for browse in other_browses:
        for interest_id in user_interest_ids:
            if interest_id != browse.product_id:
                pair = tuple(sorted((interest_id, browse.product_id)))
                product_coocur[pair] = product_coocur.get(pair, 0) + 1  # 浏览权重

    # 处理其他用户的收藏
    for collection in other_collections:
        for interest_id in user_interest_ids:
            if interest_id != collection.product_id:
                pair = tuple(sorted((interest_id, collection.product_id)))
                product_coocur[pair] = product_coocur.get(pair, 0) + 2  # 收藏权重

    # 处理其他用户的购买
    for order in other_orders:
        for interest_id in user_interest_ids:
            if interest_id != order.product_id:
                pair = tuple(sorted((interest_id, order.product_id)))
                product_coocur[pair] = product_coocur.get(pair, 0) + 3  # 购买权重

    # 计算推荐分数
    product_scores = {}
    for (pid1, pid2), count in product_coocur.items():
        if pid1 in user_interest_ids and pid2 not in user_interest_ids:
            product_scores[pid2] = product_scores.get(pid2, 0) + count
        elif pid2 in user_interest_ids and pid1 not in user_interest_ids:
            product_scores[pid1] = product_scores.get(pid1, 0) + count

    # 按分数排序，取前top_n个
    sorted_product_ids = sorted(product_scores.keys(),
                                key=lambda x: product_scores[x],
                                reverse=True)[:top_n]

    # 获取推荐商品
    recommended_products = []
    for pid in sorted_product_ids:
        product = OutdoorProduct.query.get(pid)
        if product:
            recommended_products.append(product)

    # 如果推荐商品不足，补充销量高且用户未收藏/未购买/未浏览的商品
    if len(recommended_products) < top_n:
        # 获取销量高的商品，排除用户已收藏/购买/浏览的商品
        hot_products = OutdoorProduct.query.order_by(desc('sales')).all()
        for product in hot_products:
            if product.id not in user_interest_ids and product.id not in [p.id for p in recommended_products]:
                recommended_products.append(product)
                if len(recommended_products) >= top_n:
                    break

    return recommended_products


# 获取随机商品的辅助函数
def get_random_products(count=5, exclude_id=None):
    """获取指定数量的随机商品，可以排除特定商品"""
    all_products = OutdoorProduct.query.all()

    if not all_products:
        return []

    # 如果有排除的商品，过滤掉
    if exclude_id:
        all_products = [p for p in all_products if p.id != exclude_id]

    # 如果商品数量不足，直接返回所有
    if len(all_products) <= count:
        return all_products

    # 随机选择指定数量的商品
    import random
    random_indices = random.sample(range(len(all_products)), count)
    return [all_products[i] for i in random_indices]


# 首页
@user.route("/")
def index():
    # 获取当前登录用户信息
    user_info = None
    if session.get('user_id'):
        user_info = User.query.get(session.get('user_id'))

    # 获取随机商品用于轮播图
    random_products = get_random_products(5)

    # 获取热门商品（按销量排序）
    page = request.args.get('page', 1, type=int)
    per_page = 20
    hot_products_paginate = OutdoorProduct.query.order_by(desc('sales')).paginate(
        page=page, per_page=per_page, error_out=False
    )
    hot_products = hot_products_paginate.items

    # 获取推荐商品
    recommended_products = []
    if session.get('user_id'):
        recommended_products = recommend_products(session.get('user_id'), 5)
    else:
        # 未登录用户显示销量高的商品
        recommended_products = OutdoorProduct.query.order_by(desc('sales')).limit(5).all()

    # 生成图表
    chart1 = generate_chart1()

    return render_template(
        "user/home.html",
        random_products=random_products,
        hot_products=hot_products,
        user=user_info,
        chart1=chart1,
        recommended_products=recommended_products,
        page=hot_products_paginate
    )


# 商品详情
@user.route("/detail/<int:id>")
def detail(id):
    # 获取商品信息
    product = OutdoorProduct.query.get(id)
    if not product:
        flash("商品不存在")
        return redirect(url_for('user.index'))

    # 获取当前登录用户信息
    user_info = None
    if session.get('user_id'):
        user_info = User.query.get(session.get('user_id'))

    # 获取商品评论
    comments = ProductComment.query.filter_by(product_id=id).all()
    comment_list = []
    for comment in comments:
        user = User.query.get(comment.user_id)
        if user:
            comment_list.append({
                'comment': comment,
                'name': user.name
            })

    # 获取随机推荐商品
    random_products = get_random_products(4, exclude_id=id)

    return render_template(
        "user/detail.html",
        product=product,
        comments=comment_list,
        comment_count=len(comments),
        user=user_info,
        random_products=random_products
    )


# 搜索
# 搜索函数修改
@user.route("/search", methods=['GET', 'POST'])
def search():
    # 获取当前登录用户信息
    user_info = None
    if session.get('user_id'):
        user_info = User.query.get(session.get('user_id'))

    key = ''
    products = []

    # 获取所有品牌用于下拉框
    brands = db.session.query(OutdoorProduct.derive).distinct().all()
    brand_list = [brand[0] for brand in brands if brand[0]]

    if request.method == 'POST':
        key = request.form.get('key', '').strip()
    else:  # GET方法
        key = request.args.get('keyword', '').strip()

    # 获取筛选参数
    sort_by = request.args.get('sort', 'relevance')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    brand = request.args.get('brand', '')

    # 构建查询
    query = OutdoorProduct.query

    # 关键词筛选
    if key:
        query = query.filter(
            (OutdoorProduct.name.contains(key)) | (OutdoorProduct.derive.contains(key))
        )

    # 品牌筛选
    if brand:
        query = query.filter(OutdoorProduct.derive == brand)

    # 价格范围筛选
    try:
        if min_price:
            query = query.filter(OutdoorProduct.price >= float(min_price))
        if max_price:
            query = query.filter(OutdoorProduct.price <= float(max_price))
    except ValueError:
        pass  # 如果价格不是数字，忽略价格筛选

    # 排序
    if sort_by == 'price_asc':
        query = query.order_by('price')
    elif sort_by == 'price_desc':
        query = query.order_by(desc('price'))
    elif sort_by == 'sales_desc':
        query = query.order_by(desc('sales'))
    elif sort_by == 'newest':
        query = query.order_by(desc('id'))
    # relevance 默认不排序

    products = query.all()

    return render_template(
        "user/search.html",
        products=products,
        key=key,
        user=user_info,
        brands=brand_list,
        current_sort=sort_by,
        current_brand=brand,
        min_price=min_price,
        max_price=max_price
    )


# 购物车
@user.route("/car")
def car():
    if not session.get('user_id'):
        flash("请先登录")
        return redirect(url_for('user.personal_center'))

    user_id = session.get('user_id')

    # 获取当前登录用户信息
    user_info = User.query.get(user_id)

    # 获取购物车商品
    cart_items = OrderItem.query.filter_by(
        user_id=user_id,
        is_pay=0,
        is_cancel=0
    ).all()

    cart_products = []
    total_price = 0

    for item in cart_items:
        product = OutdoorProduct.query.get(item.product_id)
        if product:
            cart_products.append({
                'product': product,
                'number': item.number,
                'item_id': item.item_id
            })
            try:
                total_price += float(product.price) * item.number
            except ValueError:
                total_price += 0

    # 获取随机推荐商品
    random_products = get_random_products(4)

    return render_template(
        "user/car.html",
        products=cart_products,
        total_price=total_price,
        user=user_info,
        random_products=random_products
    )


# 添加到购物车
@user.route("/add_car/<int:id>")
def add_car(id):
    if not session.get('user_id'):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'message': '请先登录'}), 401
        flash("请先登录")
        return redirect(url_for('user.personal_center'))

    user_id = session.get('user_id')
    product = OutdoorProduct.query.get(id)

    if not product:
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'message': '商品不存在'}), 404
        flash("商品不存在")
        return redirect(url_for('user.index'))

    # 检查是否已经在购物车中
    existing_item = OrderItem.query.filter_by(
        user_id=user_id,
        product_id=id,
        is_pay=0,
        is_cancel=0
    ).first()

    if existing_item:
        existing_item.number += 1
    else:
        new_item = OrderItem(
            product_id=id,
            user_id=user_id,
            number=1,
            is_pay=0,
            is_cancel=0
        )
        db.session.add(new_item)

    db.session.commit()

    # 如果是AJAX请求，返回JSON
    if request.headers.get('Accept') == 'application/json' or request.args.get('ajax'):
        return jsonify({'success': True, 'message': '已添加到购物车'})

    flash("已添加到购物车")
    return redirect(url_for('user.car'))


# 更新购物车商品数量
@user.route("/update_car/<int:item_id>", methods=['POST'])
def update_car(item_id):
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': '请先登录'})

    user_id = session.get('user_id')
    data = request.get_json()
    new_quantity = data.get('quantity', 1)

    if new_quantity < 1:
        return jsonify({'success': False, 'message': '数量必须大于0'})

    # 验证购物车项目属于当前用户
    cart_item = OrderItem.query.filter_by(
        item_id=item_id,
        user_id=user_id,
        is_pay=0,
        is_cancel=0
    ).first()

    if not cart_item:
        return jsonify({'success': False, 'message': '购物车项目不存在'})

    cart_item.number = new_quantity
    db.session.commit()

    # 计算新的小计
    product = OutdoorProduct.query.get(cart_item.product_id)
    if product:
        try:
            subtotal = float(product.price) * new_quantity
        except ValueError:
            subtotal = 0
    else:
        subtotal = 0

    return jsonify({
        'success': True,
        'subtotal': f'{subtotal:.2f}',
        'item_id': item_id
    })


# 从购物车删除商品
@user.route("/remove_car/<int:item_id>")
def remove_car(item_id):
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': '请先登录'}), 401

    user_id = session.get('user_id')

    # 验证购物车项目属于当前用户
    cart_item = OrderItem.query.filter_by(
        item_id=item_id,
        user_id=user_id,
        is_pay=0,
        is_cancel=0
    ).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'success': True, 'message': '商品已从购物车移除'})
    else:
        return jsonify({'success': False, 'message': '商品不存在或已被删除'}), 404


# 创建订单（支持设置订单状态）
@user.route("/create_order", methods=['POST'])
def create_order():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': '请先登录'}), 401

    user_id = session.get('user_id')

    # 获取购物车中的所有商品
    cart_items = OrderItem.query.filter_by(
        user_id=user_id,
        is_pay=0,
        is_cancel=0
    ).all()

    if not cart_items:
        return jsonify({'success': False, 'message': '购物车为空'})

    # 获取请求参数中的订单状态
    status = request.args.get('status', 'paid')  # 默认为已支付

    # 更新订单状态
    for item in cart_items:
        if status == 'paid':
            item.is_pay = 1
            item.is_cancel = 0
            # 更新商品销量
            product = OutdoorProduct.query.get(item.product_id)
            if product:
                product.sales += item.number
        elif status == 'cancelled':
            item.is_pay = 0
            item.is_cancel = 1
        elif status == 'pending':
            item.is_pay = 0
            item.is_cancel = 0

    db.session.commit()

    return jsonify({'success': True, 'message': '订单创建成功'})


# 立即购买（直接创建单个商品订单）
@user.route("/buy_now", methods=['POST'])
def buy_now():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': '请先登录'}), 401

    user_id = session.get('user_id')

    # 获取请求数据
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据格式错误'}), 400

    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    # 验证商品是否存在
    product = OutdoorProduct.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': '商品不存在'}), 404

    # 验证数量
    try:
        quantity = int(quantity)
        if quantity < 1 or quantity > 99:
            return jsonify({'success': False, 'message': '购买数量必须在1-99之间'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '购买数量格式错误'}), 400

    # 创建订单
    order_item = OrderItem(
        user_id=user_id,
        product_id=product_id,
        number=quantity,
        is_pay=1,  # 直接标记为已支付
        is_cancel=0
    )

    db.session.add(order_item)

    # 更新商品销量
    product.sales += quantity

    db.session.commit()

    return jsonify({'success': True, 'message': '购买成功'})


# 支付订单
@user.route("/pay")
def pay():
    if not session.get('user_id'):
        flash("请先登录")
        return redirect(url_for('user.login'))

    user_id = session.get('user_id')

    # 获取购物车中的所有商品
    cart_items = OrderItem.query.filter_by(
        user_id=user_id,
        is_pay=0,
        is_cancel=0
    ).all()

    if not cart_items:
        flash("购物车为空")
        return redirect(url_for('user.car'))

    # 更新订单状态和商品销量
    for item in cart_items:
        item.is_pay = 1
        product = OutdoorProduct.query.get(item.product_id)
        if product:
            product.sales += item.number

    db.session.commit()
    flash("支付成功")
    return redirect(url_for('user.personal_center'))


# 订单列表（已废弃，重定向到个人中心）
@user.route("/order")
def order():
    # 直接重定向到个人中心
    return redirect(url_for('user.personal_center'))


# 添加评论
@user.route("/add_comment/<int:id>", methods=['POST'])
def add_comment(id):
    if not session.get('user_id'):
        flash("请先登录")
        return redirect(url_for('user.login'))

    user_id = session.get('user_id')
    product = OutdoorProduct.query.get(id)

    if not product:
        flash("商品不存在")
        return redirect(url_for('user.index'))

    comment_content = request.form.get('comment', '').strip()

    if not comment_content:
        flash("请输入评论内容")
        return redirect(url_for('user.detail', id=id))

    if len(comment_content) > 5000:
        flash("评论内容过长，最多5000个字符")
        return redirect(url_for('user.detail', id=id))

    # 创建新评论
    new_comment = ProductComment(
        product_id=id,
        user_id=user_id,
        comment=comment_content
    )

    db.session.add(new_comment)
    db.session.commit()
    flash("评论添加成功")

    return redirect(url_for('user.detail', id=id))


# 登录路由
@user.route("/login", methods=['GET', 'POST'])
def login():
    # 如果已经登录，根据登录类型跳转
    if session.get('user_id'):
        if session.get('admin_id'):
            return redirect(url_for('admin.index'))
        return redirect(url_for('user.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        is_admin_login = request.form.get('admin_login') == 'on'  # 检查是否勾选管理员登录

        if not username or not password:
            flash("用户名和密码不能为空")
            return render_template("user/login.html")

        # 查找用户
        user = User.query.filter_by(name=username).first()

        # 验证密码（这里是明文比较）
        if user and user.password == password:
            session['user_id'] = user.id

            # 如果勾选了管理员登录
            if is_admin_login:
                if user.admin == 1:
                    session['admin_id'] = user.id
                    flash("管理员登录成功")
                    return redirect(url_for('admin.index'))
                else:
                    session.pop('user_id', None)  # 清除已设置的user_id
                    flash("该账户不是管理员，无法以管理员身份登录")
                    return render_template("user/login.html")
            else:
                flash("登录成功")
                return redirect(url_for('user.index'))
        else:
            flash("用户名或密码错误")

    return render_template("user/login.html")


# 注册路由
@user.route("/register", methods=['GET', 'POST'])
def register():
    # 如果已经登录，直接跳转到首页
    if session.get('user_id'):
        return redirect(url_for('user.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("用户名和密码不能为空")
            return render_template("user/register.html")

        if len(username) < 3 or len(username) > 20:
            flash("用户名长度必须在3-20个字符之间")
            return render_template("user/register.html")

        if len(password) < 6:
            flash("密码长度至少6个字符")
            return render_template("user/register.html")

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(name=username).first()
        if existing_user:
            flash("用户名已存在")
            return render_template("user/register.html")

        # 创建新用户
        new_user = User(name=username, password=password, admin=0)
        db.session.add(new_user)
        db.session.commit()

        flash("注册成功，请登录")
        return redirect(url_for('user.login'))

    return render_template("user/register.html")


# 退出登录路由
@user.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("已退出登录")
    return redirect(url_for('user.index'))


# about函数修改
@user.route("/about")
def about():
    # 获取当前登录用户信息
    user_info = None
    if session.get('user_id'):
        user_info = User.query.get(session.get('user_id'))

    # 获取所有品牌用于下拉框
    brands = db.session.query(OutdoorProduct.derive).distinct().all()
    brand_list = [brand[0] for brand in brands if brand[0]]

    # 定义分类映射
    category_map = {
        'clothing': '户外服装',
        'equipment': '户外装备',
        'tools': '户外工具',
        'all': ''
    }

    # 获取筛选参数
    keyword = request.args.get('keyword', '').strip()
    sort_by = request.args.get('sort', 'default')
    price_range = request.args.get('price_range', '')
    brand = request.args.get('brand', '')
    category_param = request.args.get('category', '')
    category = category_map.get(category_param, '')

    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # 构建查询
    query = OutdoorProduct.query

    # 分类筛选
    if category:
        query = query.filter(OutdoorProduct.category == category)

    # 关键词筛选
    if keyword:
        query = query.filter(
            (OutdoorProduct.name.contains(keyword)) | (OutdoorProduct.derive.contains(keyword))
        )

    # 品牌筛选
    if brand:
        query = query.filter(OutdoorProduct.derive == brand)

    # 价格范围筛选
    if price_range:
        try:
            if price_range == '0-100':
                query = query.filter(OutdoorProduct.price <= 100)
            elif price_range == '100-500':
                query = query.filter(OutdoorProduct.price.between(100, 500))
            elif price_range == '500-1000':
                query = query.filter(OutdoorProduct.price.between(500, 1000))
            elif price_range == '1000+':
                query = query.filter(OutdoorProduct.price >= 1000)
        except Exception as e:
            print(f"价格筛选错误: {e}")

    # 排序
    if sort_by == 'sales_desc':
        query = query.order_by(desc('sales'))
    elif sort_by == 'sales_asc':
        query = query.order_by('sales')
    elif sort_by == 'price_desc':
        query = query.order_by(desc('price'))
    elif sort_by == 'price_asc':
        query = query.order_by('price')
    else:
        query = query.order_by(OutdoorProduct.id)

    # 执行分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    return render_template(
        "user/about.html",
        products=products,
        brands=brand_list,
        page=pagination,
        user=user_info,
        current_keyword=keyword,
        current_sort=sort_by,
        current_price=price_range,
        current_brand=brand,
        current_category=category,
        current_category_param=category_param
    )


# 取消订单
@user.route("/cancel_order/<int:item_id>")
def cancel_order(item_id):
    if not session.get('user_id'):
        flash("请先登录")
        return redirect(url_for('user.login'))

    user_id = session.get('user_id')

    # 验证订单属于当前用户
    order_item = OrderItem.query.filter_by(
        item_id=item_id,
        user_id=user_id
    ).first()

    if order_item:
        # 只有未支付的订单才能取消
        if order_item.is_pay == 0:
            order_item.is_cancel = 1
            db.session.commit()
            flash("订单已取消")
        else:
            flash("已支付的订单不能取消")
    else:
        flash("订单不存在")

    return redirect(url_for('user.personal_center'))


# AJAX接口：检查用户名是否可用
@user.route("/check_username", methods=['POST'])
def check_username():
    username = request.form.get('username', '').strip()

    if not username:
        return jsonify({'available': False, 'message': '用户名不能为空'})

    if len(username) < 3 or len(username) > 20:
        return jsonify({'available': False, 'message': '用户名长度必须在3-20个字符之间'})

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(name=username).first()

    if existing_user:
        return jsonify({'available': False, 'message': '用户名已存在'})
    else:
        return jsonify({'available': True, 'message': '用户名可用'})


# AJAX接口：获取购物车商品数量
@user.route("/cart_count")
def cart_count():
    if not session.get('user_id'):
        return jsonify({'count': 0})

    user_id = session.get('user_id')
    count = OrderItem.query.filter_by(
        user_id=user_id,
        is_pay=0,
        is_cancel=0
    ).count()

    return jsonify({'count': count})


# 个人中心
@user.route("/personal_center")
def personal_center():
    # 如果未登录，显示登录表单（不重定向）
    user_info = None
    order_list = []
    collection_list = []
    browse_history_list = []

    if session.get('user_id'):
        user_id = session.get('user_id')
        user_info = User.query.get(user_id)

        # 获取用户的订单（所有状态的订单）
        orders = OrderItem.query.filter_by(user_id=user_id).all()
        for item in orders:
            product = OutdoorProduct.query.get(item.product_id)
            if product:
                order_list.append({
                    'product': product,
                    'number': item.number,
                    'item_id': item.item_id,
                    'is_cancel': item.is_cancel,
                    'is_pay': item.is_pay
                })

        # 获取用户的收藏
        collections = UserCollection.query.filter_by(user_id=user_id).all()
        for collection in collections:
            product = OutdoorProduct.query.get(collection.product_id)
            if product:
                collection_list.append({
                    'id': collection.id,
                    'product': product,
                    'created_at': collection.created_at
                })

        # 获取用户的浏览历史（最近30天，去重，按时间倒序）
        from datetime import timedelta
        thirty_days_ago = datetime.datetime.now() - timedelta(days=30)
        browse_histories = UserBrowseHistory.query.filter(
            UserBrowseHistory.user_id == user_id,
            UserBrowseHistory.browse_time >= thirty_days_ago
        ).order_by(desc(UserBrowseHistory.browse_time)).all()

        # 去重：同一商品只保留最新的浏览记录
        seen_products = set()
        for history in browse_histories:
            if history.product_id not in seen_products:
                product = OutdoorProduct.query.get(history.product_id)
                if product:
                    browse_history_list.append({
                        'id': history.id,
                        'product': product,
                        'browse_time': history.browse_time
                    })
                    seen_products.add(history.product_id)

    return render_template(
        "user/personal_center.html",
        user=user_info,
        orders=order_list,
        collections=collection_list,
        browse_histories=browse_history_list
    )


# 添加收藏
@user.route("/add_collection/<int:product_id>")
def add_collection(product_id):
    if not session.get('user_id'):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'message': '请先登录'}), 401
        flash("请先登录")
        return redirect(url_for('user.login'))

    user_id = session.get('user_id')
    product = OutdoorProduct.query.get(product_id)

    if not product:
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': False, 'message': '商品不存在'}), 404
        flash("商品不存在")
        return redirect(url_for('user.index'))

    # 检查是否已经收藏
    existing = UserCollection.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if existing:
        if request.headers.get('Accept') == 'application/json' or request.args.get('ajax'):
            return jsonify({'success': False, 'message': '已经收藏过了'})
        flash("已经收藏过了")
        return redirect(url_for('user.detail', id=product_id))

    # 创建新收藏
    new_collection = UserCollection(
        user_id=user_id,
        product_id=product_id
    )
    db.session.add(new_collection)
    db.session.commit()

    if request.headers.get('Accept') == 'application/json' or request.args.get('ajax'):
        return jsonify({'success': True, 'message': '收藏成功'})

    flash("收藏成功")
    return redirect(request.referrer or url_for('user.index'))


# 取消收藏
@user.route("/remove_collection/<int:collection_id>")
def remove_collection(collection_id):
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': '请先登录'}), 401

    user_id = session.get('user_id')

    # 验证收藏属于当前用户
    collection = UserCollection.query.filter_by(
        id=collection_id,
        user_id=user_id
    ).first()

    if collection:
        db.session.delete(collection)
        db.session.commit()
        return jsonify({'success': True, 'message': '已取消收藏'})
    else:
        return jsonify({'success': False, 'message': '收藏不存在'}), 404


# 记录浏览历史
@user.route("/record_browse/<int:product_id>")
def record_browse(product_id):
    """记录用户浏览商品的AJAX接口"""
    if not session.get('user_id'):
        return jsonify({'success': True})  # 未登录也返回成功，不影响用户体验

    user_id = session.get('user_id')
    product = OutdoorProduct.query.get(product_id)

    if not product:
        return jsonify({'success': False, 'message': '商品不存在'}), 404

    # 创建新的浏览记录（不查重，记录每次浏览）
    new_browse = UserBrowseHistory(
        user_id=user_id,
        product_id=product_id
    )
    db.session.add(new_browse)
    db.session.commit()

    return jsonify({'success': True})


# 404错误处理（已在app.py中定义，这里保留以备需要）
@user.errorhandler(404)
def page_not_found(error):
    return render_template("user/404.html"), 404


# 500错误处理
@user.errorhandler(500)
def internal_server_error(error):
    return render_template("user/500.html"), 500
