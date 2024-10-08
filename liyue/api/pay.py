# your_app_name/your_app_name/api.py

import json
import time
import datetime  # 新增导入
import random
from wechatpy.pay import WeChatPay
from wechatpy.pay.utils import calculate_signature
from wechatpy.utils import random_string
from wechatpy.exceptions import WeChatPayException
import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True)
def create_order(**kwargs):
    # 获取请求中的订单数据
    data = frappe.local.form_dict
    order_number = data.get('orderNumber')
    order_time = data.get('orderTime')
    items = data.get('items')
    total_price = data.get('totalPrice')
    address_list = data.get('addressList')
    order_type = data.get('orderType')

    # TODO: 这里可以将订单数据保存到数据库中
    # save_order_to_database(data)

    # 获取用户的 openid，需要客户端传递或在服务器端获取
    openid = data.get('openid')
    if not openid:
        return {'error': '缺少用户 openid'}

    # 如果订单类型是会员充值，保存数据到 Ly User 的子表 Ly Membership Payment
    if order_type == '会员充值':
        try:
            # 根据 openid 查询 Ly User
            user = frappe.get_doc('Ly User', {'wx_openid': openid})
        except frappe.DoesNotExistError:
            return {'error': '用户不存在'}

        # 创建新的 Ly Membership Payment 条目
        amount = total_price
        date = datetime.datetime.now()

        # 向子表添加新的记录
        user.append('table_membership_payment', {
            'amount': amount,
            'date': date
        })

        # 保存用户文档
        user.save(ignore_permissions=True)
        frappe.db.commit()

    if order_type == '商品支付':
        try:
            user = frappe.get_doc('Ly User', {'wx_openid': openid})
        except frappe.DoesNotExistError:
            return {'error': '用户不存在'}
        amount = total_price
        date = datetime.datetime.now()
        # 保存订单信息
        create_sales_order()

    # 微信支付配置
    app_id = 'wx0cdfbdd1a9a07850'
    mch_id = '1694598681'
    api_key = 'aB3dE5fG7hI9jK1LmN0pQrStUvWxYz2B'
    mch_cert = '/etc/wechatpay/apiclient_cert.pem'  # 证书路径
    mch_key = '/etc/wechatpay/apiclient_key.pem'    # 证书密钥路径
    notify_url = 'https://your-domain.com/notify'   # 微信支付结果通知接口

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
    total_fee = int(float(total_price) * 100)  # 微信支付以“分”为单位
    out_trade_no = order_number
    body = '商品支付'  # 商品描述

    # 生成随机字符串 nonce_str
    nonce_str = random_string(32)

    try:
        # 调用统一下单接口
        order = wechat_pay.order.create(
            trade_type='JSAPI',
            body=body,
            total_fee=total_fee,
            notify_url=notify_url,
            out_trade_no=out_trade_no,
            user_id=openid,
            nonce_str=nonce_str
        )

        # 获取 prepay_id
        prepay_id = order.get('prepay_id')
        if not prepay_id:
            return {'error': '无法获取 prepay_id'}

        # 生成支付参数
        timeStamp = str(int(time.time()))
        package = f"prepay_id={prepay_id}"
        signType = 'MD5'

        # 构造签名所需参数
        pay_data = {
            'appId': app_id,
            'timeStamp': timeStamp,
            'nonceStr': nonce_str,
            'package': package,
            'signType': signType,
        }

        # 生成支付签名
        paySign = calculate_signature(pay_data, api_key)

        payment_data = {
            'paymentData': {
                'timeStamp': timeStamp,
                'nonceStr': nonce_str,
                'package': package,
                'signType': signType,
                'paySign': paySign
            }
        }

        return payment_data

    except WeChatPayException as e:
        frappe.log_error(message=str(e), title="WeChat Pay Error")
        return {
            'error': '微信支付下单失败',
            'detail': str(e)
        }


def create_sales_order():
    # 创建 Ly Sales Order 文档实例
    sales_order = frappe.get_doc({
        "doctype": "Ly Sales Order",
        "customer": "LY-USER-2024-00019",  # 替换为实际的客户名称或ID
        "status": "已支付",
        "order_date": now_datetime(),  # 或者使用实际的订单日期
        "total_amount": 1500.00,  # 订单总金额
        "order_item": [
            {
                "doctype": "Ly Order Item",
                "item_code": "ITEM001",
                "item_name": "商品A",
                "qty": 2,
                "rate": 500.00,
                "amount": 1000.00
            },
            {
                "doctype": "Ly Order Item",
                "item_code": "ITEM002",
                "item_name": "商品B",
                "qty": 1,
                "rate": 500.00,
                "amount": 500.00
            }
        ],
        "form_generation": [
            {
                "doctype": "Ly Form Generation",
                "form_name": "表单1",
                "form_data": "表单内容1"
            },
            {
                "doctype": "Ly Form Generation",
                "form_name": "表单2",
                "form_data": "表单内容2"
            }
        ]
    })

    # 保存文档
    sales_order.insert()
    frappe.db.commit()
    print(f"订单已成功创建，订单号为: {sales_order.name}")
