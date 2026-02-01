# Flask户外商品商城系统

一个功能完整的户外商品电子商务平台，使用Flask框架开发，支持用户购物、订单管理和管理后台功能。

## 📸 项目截图

![项目封面](https://source.unsplash.com/1600x900/?outdoor,camping,hiking)

## ✨ 功能特点

### 用户端功能
- **用户认证**：注册、登录、退出
- **商品浏览**：首页推荐、商品列表、商品搜索
- **商品详情**：查看详细信息、图片展示、用户评价
- **购物车**：添加商品、修改数量、删除商品、实时价格计算
- **立即购买**：快速下单，无需加入购物车
- **订单管理**：
  - 订单创建（已支付、待支付、已取消）
  - 订单状态筛选
  - 再次购买功能
- **个人中心**：
  - 浏览历史
  - 订单记录
  - 收藏商品
- **浏览历史**：自动记录用户浏览过的商品

### 管理后台功能
- **仪表盘**：数据统计、图表展示
- **商品管理**：
  - 添加/编辑/删除商品
  - 商品分类管理
  - 库存管理
  - 销量统计
- **订单管理**：
  - 查看所有订单
  - 订单状态管理
  - 订单详情查看
- **用户管理**：
  - 查看用户列表
  - 用户信息管理

## 🛠️ 技术栈

### 后端
- **框架**：Flask 3.x
- **ORM**：SQLAlchemy
- **数据库驱动**：PyMySQL
- **数据库**：MySQL 5.7+

### 前端
- **基础**：HTML5 + CSS3 + JavaScript ES6
- **库**：jQuery
- **UI**：自定义响应式设计
- **动画**：CSS3 Animations + Transitions

### 项目结构
```
python_flask/
├── app/
│   ├── __init__.py          # Flask应用初始化
│   ├── app.py               # 应用配置
│   ├── models.py            # 数据库模型
│   ├── admin/               # 管理后台蓝图
│   │   ├── __init__.py
│   │   └── view.py          # 管理后台路由
│   ├── user/                # 用户端蓝图
│   │   ├── __init__.py
│   │   └── view.py          # 用户端路由
│   ├── templates/           # Jinja2模板
│   │   ├── admin/           # 管理后台模板
│   │   └── user/            # 用户端模板
│   ├── static/              # 静态文件
│   │   ├── css/             # 样式文件
│   │   ├── js/              # JavaScript文件
│   │   └── icons/           # 图标资源
│   └── utils/               # 工具模块
├── app_start.py             # 应用启动文件
├── add_browse_history_table.py  # 数据库迁移脚本
├── add_category_column.py   # 数据库迁移脚本
└── requirements.txt         # Python依赖
```

## 📦 安装说明

### 环境要求
- Python 3.8+
- MySQL 5.7+
- pip

### 1. 克隆项目
```bash
git clone https://github.com/yuxuan0502/python-flask-outdoor-store.git
cd python-flask-outdoor-store
```

### 2. 安装依赖
```bash
pip install flask pymysql sqlalchemy
```

或使用requirements.txt（推荐）：
```bash
pip install -r requirements.txt
```

### 3. 数据库配置

创建数据库：
```sql
CREATE DATABASE outdoor_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `app/app.py` 中的数据库配置：
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://用户名:密码@localhost:端口/数据库名'
```

### 4. 导入数据（可选）
```bash
python app/utils/import_db.py
```

### 5. 创建管理员账号
```bash
python app/admin/create_admin.py
```

## 🚀 运行项目

```bash
python app_start.py
```

访问：
- 用户端：http://localhost:5050
- 管理后台：http://localhost:5050/admin

## 📱 页面路由

### 用户端
| 路由 | 功能 |
|------|------|
| `/` | 首页 |
| `/login` | 登录 |
| `/register` | 注册 |
| `/about` | 全部商品 |
| `/detail/<id>` | 商品详情 |
| `/search` | 商品搜索 |
| `/car` | 购物车 |
| `/personal_center` | 个人中心 |
| `/buy_now` | 立即购买 |

### 管理后台
| 路由 | 功能 |
|------|------|
| `/admin/login` | 管理员登录 |
| `/admin/home` | 后台首页 |
| `/admin/item` | 商品管理 |
| `/admin/order` | 订单管理 |
| `/admin/user` | 用户管理 |

## 🎨 主要特性

### UI/UX设计
- 🎨 现代化渐变色设计
- 📱 完全响应式布局
- ✨ 流畅的动画效果
- 🖱️ 友好的交互体验

### 核心功能
- 🔐 完整的用户认证系统
- 🛒 实时购物车价格计算
- 💳 多种订单状态管理
- 📊 数据统计和图表展示
- 🔍 智能商品搜索

## 🐛 已知问题

- 浏览器缓存可能导致样式更新延迟，请使用 Ctrl+F5 强制刷新

## 📝 更新日志

### v1.0.0 (2024)
- ✅ 初始版本发布
- ✅ 用户注册登录功能
- ✅ 商品浏览和搜索
- ✅ 购物车功能
- ✅ 订单系统
- ✅ 个人中心
- ✅ 管理后台
- ✅ 立即购买功能

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👨‍💻 作者

yuxuan0502 - [GitHub](https://github.com/yuxuan0502)

## 🙏 致谢

感谢所有开源项目的贡献者！

---

⭐ 如果这个项目对你有帮助，请给一个Star！
