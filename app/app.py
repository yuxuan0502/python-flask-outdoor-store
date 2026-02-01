import os
from flask import Flask, render_template, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

# 数据库配置 - 从环境变量读取，支持Vercel部署
database_url = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:123456@127.0.0.1:3307/flask_outdoor_store?charset=utf8'
)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# 密钥配置，在生产环境中使用系统自动生成
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'd890fbe7e26c4c3eb557b6009e3f4d3d')
app.app_context().push()

app.debug = True

# 注册数据模型
db = SQLAlchemy(app)

# 延迟导入蓝图（避免循环导入）
def register_blueprints():
    # 导入并注册蓝图
    from app.admin import admin as admin_blueprint
    from app.user import user as user_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(user_blueprint, url_prefix='/')

# 立即注册蓝图
register_blueprints()

# 6. 404错误处理
@app.errorhandler(404)
def page_not_found(error):
    return render_template("user/404.html"), 404

# 7. 前置请求处理
@app.before_request
def before_request():
    session.permanent = True

# 健康检查路由 - 用于Vercel部署测试
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Flask应用运行正常'})

# 根路径欢迎页面
@app.route('/api')
def api_info():
    return jsonify({
        'status': 'ok',
        'message': 'Flask户外商品商城API',
        'version': '1.0.0',
        'database': 'connected' if db.engine else 'not configured'
    })

# 8. 自动创建数据库表（仅在本地环境）
# Vercel部署时跳过自动创建表
if os.getenv('VERCEL') != '1':
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("应用将在无数据库模式下运行")


