from app.app import db
from app.models import OutdoorProduct
import csv


def assign_category(product_name):
    """根据商品名称自动分配分类"""
    # 户外服装：手套、袜子、帽子、衣服、裤子、鞋子、瑜伽服等穿戴类
    clothing_keywords = ['手套', '袜子', '帽', '衣', '裤', '鞋', '服', '睡袋', '帐篷', '背包', '户外服', '冲锋衣', '速干', '登山服']
    # 户外工具：指南针、照明灯、刀具等工具类
    tool_keywords = ['指南针', '指北针', '灯', '照明', '刀具', '工具']
    # 户外装备：水具、炊具、配件等装备类
    equipment_keywords = ['水杯', '水壶', '水袋', '饮水袋', '口水壶', '淋浴袋', '沐浴袋', '酒壶', '电热水杯', '炊具', '炉具', '套锅']

    # 先检查是否是服装（包含服、衣、裤等穿戴关键词）
    for keyword in clothing_keywords:
        if keyword in product_name:
            return '户外服装'

    # 再检查是否是工具
    for keyword in tool_keywords:
        if keyword in product_name:
            return '户外工具'

    # 再检查是否是装备（水具等）
    for keyword in equipment_keywords:
        if keyword in product_name:
            return '户外装备'

    # 默认为装备
    return '户外装备'


def import_csv_to_db(csv_path):
    # CSV字段需要包含：name, price, derive, sales, photo
    try:
        # 把导入代码中打开文件的代码改成下面这样
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # 先打印CSV的表头，确认是否匹配
            print("CSV表头：", reader.fieldnames)
            # 打印CSV的行数，确认有数据
            row_count = sum(1 for row in reader)
            print(f"CSV中共有{row_count}条数据")
            # 重新定位到文件开头，继续读取
            f.seek(0)
            next(reader)  # 跳过表头

            for idx, row in enumerate(reader, 1):
                product = OutdoorProduct()
                product.name = row.get('name', '')
                product.price = row.get('price', '')
                product.derive = row.get('derive', '')
                product.sales = int(row.get('sales', 0))
                product.photo = row.get('photo', '')
                # 自动分配分类
                product.category = assign_category(product.name)
                db.session.add(product)
                print(f"正在导入第{idx}条数据：{product.name} (分类：{product.category})")

        db.session.commit()
        print("数据全部导入成功！")
        return True
    except FileNotFoundError:
        print(f"错误：找不到CSV文件，请检查路径是否正确：{csv_path}")
        return False
    except ValueError as e:
        db.session.rollback()  # 出错回滚事务
        print(f"错误：数据类型转换失败（比如sales不是数字）：{str(e)}")
        return False
    except Exception as e:
        db.session.rollback()  # 出错回滚事务
        print(f"导入失败：{str(e)}")
        return False

if __name__ == '__main__':
    import_csv_to_db(r'E:\PYCHARM\毕\python_flask\app\utils\products.csv')