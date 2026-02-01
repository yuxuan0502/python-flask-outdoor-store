from flask import Blueprint

user = Blueprint(
    'user',
    __name__,
    template_folder='../templates/user',  # 修正为相对路径
    static_folder='../static/user'  # 修正为相对路径
)

from . import view
