import os
import google.generativeai as genai

# 配置代理（与 main.py 一致）
os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:7897")
os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")

# 使用环境变量或占位符 Key
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyB4Pl_P21RbWVXqt3V6u2rMLQZI4itFLVI")

def test_gemini():
    print(f"正在配置 API Key: {API_KEY[:10]}...")
    genai.configure(api_key=API_KEY)
    
    print("正在列出可用模型...")
    try:
        models = genai.list_models()
        model_names = [m.name for m in models]
        print(f"可用模型列表: {model_names}")
        
        target = "models/gemini-2.5-flash"
        if target in model_names:
            print(f"✅ 成功找到目标模型: {target}")
            
            # 尝试简单生成
            print("正在尝试简单生成测试...")
            model = genai.GenerativeModel("gemini-2.5-flash")
            res = model.generate_content("你好，请回复 '连接成功'")
            print(f"模型回复: {res.text}")
        else:
            print(f"❌ 未找到目标模型: {target}")
            # 尝试查找包含 flash 的模型
            flashes = [n for n in model_names if "flash" in n.lower()]
            print(f"建议使用的 Flash 模型: {flashes}")
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    test_gemini()
