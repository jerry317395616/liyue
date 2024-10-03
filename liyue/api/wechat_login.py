import frappe
import requests


@frappe.whitelist(allow_guest=True)
def wechat_login():
	# 获取传递的 code 参数
	code = frappe.form_dict.get('code')

	if not code:
		frappe.throw("Missing 'code' parameter")
	# 获取微信小程序的 AppID 和 AppSecret
	# app_id = frappe.db.get_single_value('Wechat Settings', 'app_id')
	# app_secret = frappe.db.get_single_value('Wechat Settings', 'app_secret')

	# 3a4d8a2b4fdd63bd3b84681d02988572
	app_id = 'wx0cdfbdd1a9a07850'
	app_secret = '3a4d8a2b4fdd63bd3b84681d02988572'
	# app_secret = '87e7e144939bee97bfe3485a7f83c32c'

	# 微信登录 API URL
	url = "https://api.weixin.qq.com/sns/jscode2session"

	# 请求参数
	params = {
		"appid": app_id,
		"secret": app_secret,
		"js_code": code,
		"grant_type": "authorization_code"
	}

	# 向微信服务器请求 session_key 和 openid
	response = requests.get(url, params=params)
	result = response.json()
	# return result
	if 'openid' in result:
		openid = result['openid']
		session_key = result['session_key']
		# 根据 openid 创建或获取用户
		user = get_or_create_user(openid)

		# 如果用户存在，则生成 token 并返回
		if user:
			token = frappe.generate_hash(length=32)

			# 保存 token（可选：如果你希望在服务器端验证 token）
			frappe.cache().set_value(f"token_{user.name}", token)

			return {
				"token": token,
				"user_id": user.name,
				"openid": openid,
				"session_key": session_key
			}
		else:
			# 用户不存在，返回空的 token 和 user_id
			return {
				"token": "",
				"user_id": "",
				"openid": openid,
				"session_key": session_key
			}
	else:
		frappe.throw("WeChat login failed")


def get_or_create_user(openid):
	# 查找用户是否已经存在
	user_name = frappe.db.get_value("Ly User", {"wx_openid": openid}, "name")

	if not user_name:
		# 如果用户不存在，直接返回 None
		return None
	else:
		return frappe.get_doc("Ly User", user_name)
