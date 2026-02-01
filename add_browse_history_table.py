"""
创建用户浏览历史表
"""
from app.app import db
from sqlalchemy import text


def create_browse_history_table():
    """创建用户浏览历史表"""
    try:
        with db.engine.connect() as conn:
            # 检查表是否已存在
            check_table = conn.execute(text("""
                SELECT COUNT(*) as count FROM information_schema.tables
                WHERE table_name = 'user_browse_history'
            """)).fetchone()

            if check_table[0] > 0:
                print("表 user_browse_history 已存在，跳过创建")
                return True

            # 创建浏览历史表
            conn.execute(text("""
                CREATE TABLE user_browse_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    product_id INT NOT NULL,
                    browse_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES outdoor_product(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_product_id (product_id),
                    INDEX idx_browse_time (browse_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """))

            conn.commit()
            print("浏览历史表 user_browse_history 创建成功！")
            return True

    except Exception as e:
        print(f"操作失败: {str(e)}")
        return False


if __name__ == '__main__':
    print("开始创建浏览历史表...")
    create_browse_history_table()
