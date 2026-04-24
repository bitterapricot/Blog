import os
import sys
import json
import requests
import traceback
from datetime import datetime

def call_api(api_url, hf_token, test_mode=False):
    """
    调用目标 API
    """
    try:
        headers = {
            "User-Agent": "GitHub-Actions-API-Checker/1.0",
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        
        # 根据你的 API 需求调整参数
        params = {}
        if test_mode == 'true':
            params['test'] = 'true'
            print("🔧 测试模式已启用")
        
        print(f"🌐 调用 API: {api_url}")
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        
        result = {
            'status': response.status_code,
            'headers': dict(response.headers),
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'success': response.status_code == 200,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'url': api_url
        }
        
        print(f"✅ API 调用成功，状态码: {response.status_code}")
        return result
        
    except requests.exceptions.Timeout:
        return {
            'status': 408,
            'error': '请求超时',
            'success': False,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 500,
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'status': 500,
            'error': f'未知错误: {str(e)}',
            'success': False,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def send_to_wechat(webhook_url, api_result):
    """
    发送消息到企业微信
    """
    try:
        # 构建消息内容
        if api_result.get('success'):
            status_emoji = "✅"
            status_text = "成功"
        else:
            status_emoji = "❌"
            status_text = "失败"
        
        # 创建 Markdown 格式消息
        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"""## API 每日检查报告 {status_emoji}
                
**状态**: {status_text}
**时间**: {api_result.get('timestamp', 'N/A')}
**API URL**: {api_result.get('url', 'N/A')}
**HTTP 状态码**: {api_result.get('status', 'N/A')}

### 响应详情：{json.dumps(api_result.get('data', {}), indent=2, ensure_ascii=False)}
**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**触发方式**: {os.environ.get('GITHUB_EVENT_NAME')}"""
            }
        }
        
        # 如果有错误信息，添加到消息中
        if not api_result.get('success'):
            error_msg = api_result.get('error', '未知错误')
            message['markdown']['content'] += f"\n\n**错误信息**: {error_msg}"
        
        # 发送到企业微信
        response = requests.post(
            webhook_url,
            json=message,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ 消息已发送到企业微信")
            return True
        else:
            print(f"❌ 发送到企业微信失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发送消息时出错: {str(e)}")
        traceback.print_exc()
        return False

def main():
    # 从环境变量获取配置
    HF_TOKEN = os.getenv("HUGGINGFACE_READ_ACCESS_TOKEN")
    api_url = "https://bitterapricot-xtools.hf.space/appfast/info" #os.getenv('API_URL')
    webhook_url = os.getenv('WECHAT_WEBHOOK_URL')
    test_mode = os.getenv('TEST_MODE', 'false')
    
    if not api_url or not webhook_url:
        print("❌ 请设置 API_URL 和 WECHAT_WEBHOOK_URL 环境变量")
        sys.exit(1)
    
    print(f"🚀 开始 API 检查任务...")
    print(f"🔧 测试模式: {test_mode}")
    
    # 1. 调用 API
    api_result = call_api(api_url, HF_TOKEN, test_mode)
    
    # 2. 记录日志
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'api_result': api_result,
        'test_mode': test_mode
    }
    
    # 3. 发送到企业微信
    send_success = send_to_wechat(webhook_url, api_result)
    
    api_result = call_api("https://bitterapricot-node.hf.space/appfast/info", HF_TOKEN, test_mode)
    send_success = send_to_wechat(webhook_url, api_result)

    api_result = call_api("https://bitterapricot-priapp.hf.space/appfast/info", HF_TOKEN, test_mode)
    send_success = send_to_wechat(webhook_url, api_result) 

    api_result = call_api("https://bitterapricot-fastapi.hf.space/appfast/info", HF_TOKEN, test_mode)
    send_success = send_to_wechat(webhook_url, api_result)   
    
    api_result = call_api("https://bitterapricot-flaskapi.hf.space/appfast/info", HF_TOKEN, test_mode)
    send_success = send_to_wechat(webhook_url, api_result)   
    
    api_result = call_api("https://bitterapricot-napi.hf.space/appfast/info", HF_TOKEN, test_mode)
    send_success = send_to_wechat(webhook_url, api_result)   

    api_result = call_api("https://xtumu-template.hf.space/appfast/info", HF_TOKEN, test_mode)
    send_success = send_to_wechat(webhook_url, api_result)   
    
    if send_success and api_result.get('success'):
        print("🎉 任务完成！")
        sys.exit(0)
    else:
        print("⚠️ 任务完成，但有警告")
        sys.exit(1)

if __name__ == "__main__":
    main()
