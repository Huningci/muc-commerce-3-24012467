import unittest
import json
import sys
import os

# 【关键修改】这三行代码的作用是告诉 Python：
# “请去我所在文件夹的上一级目录（..）里找代码”
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 现在这行就能正常工作了
from app import app 

class TestFlaskAPI(unittest.TestCase):

    def setUp(self):
        """每次测试前初始化"""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
        # 模拟登录用的账号密码（请根据你 login.html 里的实际账号修改）
        self.login_data = {
            'username': 'student', 
            'password': 'day07'
        }

    def test_health_check(self):
        """1. 测试 /health 接口是否返回 200"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        print("✅ /health 检查通过")

    def test_metrics_unauthorized(self):
        """2. 测试未登录访问 /api/metrics 是否被拦截"""
        # 先清除可能存在的 session，模拟未登录状态
        with self.client.session_transaction() as sess:
            sess.clear()
            
        response = self.client.get('/api/metrics')
        # 通常 @login_required 会返回 302 重定向到登录页，或者 401
        self.assertIn(response.status_code, [302, 401]) 
        print("✅ 未登录拦截检查通过")

    def test_metrics_authorized(self):
        """3. 测试登录后访问 /api/metrics 是否正常"""
        # 模拟登录过程
        self.client.post('/login', data=self.login_data, follow_redirects=True)
        
        # 访问接口
        response = self.client.get('/api/metrics')
        
        # 检查状态码是否为 200
        self.assertEqual(response.status_code, 200)
        
        # 检查返回的数据是否包含 "ok" (根据你的代码 return jsonify({"ok": ...}))
        data = json.loads(response.data)
        self.assertIn('ok', data)
        print("✅ 登录后数据获取检查通过")

    def test_categories_filter(self):
        """4. 测试 /api/categories?category=Fashion 筛选功能"""
        # 先登录
        self.client.post('/login', data=self.login_data, follow_redirects=True)
        
        # 带参数访问
        response = self.client.get('/api/categories?category=Fashion')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # 检查返回的数据里是否包含 ok 字段
        self.assertIn('ok', data)
        print("✅ 分类筛选检查通过")

if __name__ == '__main__':
    unittest.main()