# Vercel Serverless Function for Flask
import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.app import app

# Vercel需要这个处理器
def handler(request):
    return app(request.environ, start_response)
