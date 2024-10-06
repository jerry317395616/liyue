# your_app_name/your_app_name/api.py

import json
import time
import random
from wechatpy.pay import WeChatPay
from wechatpy.pay.utils import calculate_signature
from wechatpy.exceptions import WeChatPayException
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def create_order(**kwargs):
    # 获取请求中的订单数据
    data = frappe.local.form_dict
    order_number = data.get('orderNumber')
    order_time = data.get('orderTime')
    items = data.get('items')
    total_price = data.get('totalPrice')
    address_list = data.get('addressList')

    # TODO: 这里可以将订单数据保存到数据库中
    # save_order_to_database(data)

    # 微信支付配置
    app_id = 'wx0cdfbdd1a9a07850'
    mch_id = '1694598681'
    api_key = 'aB3dE5fG7hI9jK1LmN0pQrStUvWxYz2B'
    mch_cert = '/Users/kakaxi/cert/1694598681_20241006_cert/apiclient_cert.pem'  # 证书路径
    mch_key = '/Users/kakaxi/cert/1694598681_20241006_cert/apiclient_key.pem'    # 证书密钥路径
    notify_url = 'https://your-domain.com/notify'  # 微信支付结果通知接口

    # 初始化 WeChatPay 对象
    wechat_pay = WeChatPay(
        appid=app_id,
        api_key=api_key,
        mch_id=mch_id,
        mch_cert=mch_cert,
        mch_key=mch_key,
        timeout=30
    )

    # 生成微信支付统一下单所需的参数
    total_fee = int(float(total_price) * 100)  # 微信支付以分为单位
    out_trade_no = order_number
    body = '商品支付'  # 商品描述

    # 获取用户的 openid，需要客户端传递或在服务器端获取
    openid = data.get('openid')
    if not openid:
        return {'error': '缺少用户 openid'}

    try:
        # 调用统一下单接口
        order = wechat_pay.order.create(
            trade_type='JSAPI',
            body=body,
            total_fee=total_fee,
            notify_url=notify_url,
            out_trade_no=out_trade_no,
            user_id=openid
        )

        # 生成支付参数
        timeStamp = str(int(time.time()))
        nonceStr = wechat_pay.pay.nonce_str
        package = f"prepay_id={order.get('prepay_id')}"
        signType = 'MD5'
        paySign = calculate_signature({
            'appId': app_id,
            'timeStamp': timeStamp,
            'nonceStr': nonceStr,
            'package': package,
            'signType': signType,
        }, api_key)

        payment_data = {
            'timeStamp': timeStamp,
            'nonceStr': nonceStr,
            'package': package,
            'signType': signType,
            'paySign': paySign
        }

        return {
            'paymentData': payment_data
        }
    except WeChatPayException as e:
        frappe.log_error(message=str(e), title="WeChat Pay Error")
        return {
            'error': '微信支付下单失败',
            'detail': str(e)
        }