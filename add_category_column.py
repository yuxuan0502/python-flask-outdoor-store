"""
添加category字段到outdoor_product表
运行此脚本来更新数据库表结构
"""
from app.app import db
from sqlalchemy import text


def add_category_column():
    """添加category列到outdoor_product表"""
    try:
        with db.engine.connect() as conn:
            # 检查列是否已存在
            result = conn.execute(text("SHOW COLUMNS FROM outdoor_product LIKE 'category'"))
            if result.fetchone():
                print("category列已存在，无需添加")
                return True

            # 添加category列
            print("正在添加category列到outdoor_product表...")
            conn.execute(text(
                "ALTER TABLE outdoor_product "
                "ADD COLUMN category VARCHAR(50) DEFAULT '其他装备' "
                "AFTER sales"
            ))
            conn.commit()
            print("category列添加成功！")

            # 更新现有数据的分类
            print("\n正在更新现有商品数据的分类...")

            # 获取所有商品
            products = conn.execute(text("SELECT id, name FROM outdoor_product")).fetchall()

            category_count = {'骑行手套': 0, '户外水具': 0, '其他装备': 0}

            for product_id, name in products:
                category = assign_category(name)
                conn.execute(text(
                    "UPDATE outdoor_product SET category = :category WHERE id = :id"
                ), {'category': category, 'id': product_id})
                category_count[category] += 1
                print(f"商品ID {product_id}: {name[:30]}... -> {category}")

            conn.commit()
            print("\n分类更新成功！")
            print("\n分类统计:")
            for category, count in category_count.items():
                print(f"  {category}: {count} 个商品")

            return True

    except Exception as e:
        print(f"操作失败: {str(e)}")
        return False


def assign_category(product_name):
    """根据商品名称自动分配分类"""
    if '手套' in product_name:
        return '骑行手套'
    elif any(keyword in product_name for keyword in ['水杯', '水壶', '水袋', '饮水袋', '口水壶', '淋浴袋', '沐浴袋', '酒壶', '电热水杯']):
        return '户外水具'
    else:
        return '其他装备'


if __name__ == '__main__':
    print("开始添加category字段...")
    add_category_column()
