import frappe
import requests
import base64
import json
from Crypto.Cipher import AES

@frappe.whitelist()
def wechat_login(code, phone):
    # 使用 code 换取 session_key 和 openid
    appid = 'wx0cdfbdd1a9a07850'
    secret = '3a4d8a2b4fdd63bd3b84681d02988572'
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'

    response = requests.get(url)
    data = response.json()

    if 'errcode' in data:
        frappe.throw(data.get('errmsg'))

    openid = data.get('openid')
    session_key = data.get('session_key')

    # 根据 openid 查找或创建用户
    user = get_or_create_user(openid, phone)

    # 返回必要的信息给前端
    return {
        'openid': openid,
        'session_key': session_key,
        'user_id': user.name,
        'token': user.api_key  # 假设您使用 API Key 作为 token
    }

def get_or_create_user(openid, phone):
    # 尝试查找已有用户
    user_list = frappe.get_all('User', filters={'openid': openid}, limit=1)
    if user_list:
        return frappe.get_doc('User', user_list[0].name)
    else:
        # 创建新用户
        new_user = frappe.get_doc({
            'doctype': 'User',
            'email': f'{openid}@weixin.qq.com',
            'first_name': 'WeChat User',
            'openid': openid,
            'phone': phone,
            'username': openid,
            'enabled': 1,
            'new_password': frappe.generate_hash(openid),
            'user_type': 'Website User',
            'api_key': frappe.generate_hash(length=15),
        })
        new_user.flags.ignore_permissions = True
        new_user.insert()
        return new_user

@frappe.whitelist()
def wechat_decrypt_phone(code, encryptedData, iv):
    # 使用 code 换取 session_key
    appid = 'wx0cdfbdd1a9a07850'
    secret = '3a4d8a2b4fdd63bd3b84681d02988572'
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'

    response = requests.get(url)
    data = response.json()

    if 'errcode' in data:
        frappe.throw(data.get('errmsg'))

    session_key = data.get('session_key')

    # 解密数据
    decrypted_data = decrypt(encryptedData, iv, session_key, appid)

    phone_number = decrypted_data.get('phoneNumber')

    if phone_number:
        return {
            'phoneNumber': phone_number
        }
    else:
        frappe.throw('解密手机号失败')

def decrypt(encryptedData, iv, sessionKey, appId):
    # Base64 解码
    sessionKey = base64.b64decode(sessionKey)
    encryptedData = base64.b64decode(encryptedData)
    iv = base64.b64decode(iv)

    # 解密
    cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encryptedData)

    # 去除补位字符
    decrypted = unpad(decrypted)
    decrypted = json.loads(decrypted.decode('utf-8'))

    if decrypted.get('watermark', {}).get('appid') != appId:
        frappe.throw('解密失败，AppID 不匹配')

    return decrypted

def unpad(s):
    return s[:-ord(s[len(s)-1:])]
