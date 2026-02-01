import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import app, db
from app.models import User
from werkzeug.security import generate_password_hash


def create_admin():
    with app.app_context():
        # 检查是否已存在管理员
        existing_admin = User.query.filter_by(admin=1).first()
        if existing_admin:
            print(f"管理员已存在: {existing_admin.name}")
            return

        # 创建管理员账户
        admin_user = User(
            name='admin',
            password='admin123',  # 明文密码，登录后请立即修改
            admin=1  # 1 表示管理员
        )

        db.session.add(admin_user)
        db.session.commit()
        print("管理员账户创建成功!")
        print("用户名: admin")
        print("密码: admin123")
        print("请登录后立即修改密码!")


if __name__ == '__main__':
    create_admin()