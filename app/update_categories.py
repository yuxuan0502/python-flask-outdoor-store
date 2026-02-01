"""
更新现有商品数据的分类字段
运行此脚本后，数据库中的所有商品将根据名称自动分配分类
"""
from app.app import db
from app.models import OutdoorProduct


def assign_category(product_name):
    """根据商品名称自动分配分类"""
    if '手套' in product_name:
        return '骑行手套'
    elif any(keyword in product_name for keyword in ['水杯', '水壶', '水袋', '饮水袋', '口水壶', '淋浴袋', '沐浴袋', '酒壶', '电热水杯']):
        return '户外水具'
    else:
        return '其他装备'


def update_all_categories():
    """更新所有商品的分类"""
    try:
        # 获取所有商品
        products = OutdoorProduct.query.all()
        print(f"找到 {len(products)} 个商品")

        # 统计各分类数量
        category_count = {'骑行手套': 0, '户外水具': 0, '其他装备': 0}

        for product in products:
            old_category = getattr(product, 'category', None)
            new_category = assign_category(product.name)
            product.category = new_category
            category_count[new_category] += 1
            print(f"商品: {product.name[:30]}... -> 分类: {new_category}")

        db.session.commit()
        print("\n分类更新成功！")
        print("\n分类统计:")
        for category, count in category_count.items():
            print(f"  {category}: {count} 个商品")

        return True
    except Exception as e:
        db.session.rollback()
        print(f"更新失败: {str(e)}")
        return False


if __name__ == '__main__':
    print("开始更新商品分类...")
    update_all_categories()
