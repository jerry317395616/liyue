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
    attach_data = order_type
    user_id = data.get('user_id')
    my_notify_url = 'https://liyue.nanhengliyue.com/api/method/liyue.api.pay.wechat_pay_notify'
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
        my_notify_url = 'https://liyue.nanhengliyue.com/api/method/liyue.api.pay.wechat_pay_notify_member'
        # 向子表添加新的记录
        user.append('table_membership_payment', {
            'amount': amount,
            'date': date,
			'order_number':order_number,
			'pay_state':'待支付'
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
        create_sales_order(user_id,amount,order_number,items,address_list)

    # 微信支付配置
    app_id = 'wx0cdfbdd1a9a07850'
    mch_id = '1694598681'
    api_key = 'aB3dE5fG7hI9jK1LmN0pQrStUvWxYz2B'
    mch_cert = '/etc/wechatpay/apiclient_cert.pem'  # 证书路径
    mch_key = '/etc/wechatpay/apiclient_key.pem'    # 证书密钥路径
    notify_url = my_notify_url   # 微信支付结果通知接口

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
            nonce_str=nonce_str,
            attach=attach_data
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


def create_sales_order(customer,total_amount,order_number,items,address_list):
    # 创建 Ly Sales Order 文档实例
    sales_order = frappe.get_doc({
        "doctype": "Ly Sales Order",
        "customer": customer,  # 替换为实际的客户名称或ID
        "status": "待支付",
        "order_date": now_datetime(),  # 或者使用实际的订单日期
        "total_amount": total_amount,  # 订单总金额
        "order_number": order_number,
        "order_item": items,
        "form_generation": address_list
    })

    # 保存文档
    sales_order.insert()
    frappe.db.commit()



@frappe.whitelist(allow_guest=True)
def wechat_pay_notify():
    # 获取微信发送的支付结果通知数据（XML 格式）
    try:
        # 从请求中获取原始的 XML 数据
        xml_data = frappe.request.data
        # 将 XML 数据解析为字典
        wechat_pay = get_wechat_pay_client()
        result_data = wechat_pay.parse_payment_result(xml_data)

        # 验证签名
        if result_data['return_code'] == 'SUCCESS' and result_data['result_code'] == 'SUCCESS':
            out_trade_no = result_data['out_trade_no']  # 商户订单号
            transaction_id = result_data['transaction_id']  # 微信支付订单号
            total_fee = result_data['total_fee']  # 订单金额，单位为分
            openid = result_data['openid']  # 用户标识

            # 根据商户订单号查询订单并更新状态
            update_order_status(out_trade_no, transaction_id, total_fee, openid)

            # 返回成功响应给微信服务器
            return wechat_success_response()
        else:
            # 处理失败的情况
            error_message = result_data.get('return_msg', 'Unknown error')
            frappe.log_error(message=error_message, title="WeChat Pay Notify Error")
            return wechat_fail_response(error_message)
    except WeChatPayException as e:
        frappe.log_error(message=str(e), title="WeChat Pay Exception")
        return wechat_fail_response(str(e))
    except Exception as e:
        frappe.log_error(message=str(e), title="WeChat Pay Notify Exception")
        return wechat_fail_response(str(e))


@frappe.whitelist(allow_guest=True)
def wechat_pay_notify_member():
    # 获取微信发送的支付结果通知数据（XML 格式）
    try:
        # 从请求中获取原始的 XML 数据
        xml_data = frappe.request.data
        # 将 XML 数据解析为字典
        wechat_pay = get_wechat_pay_client()
        result_data = wechat_pay.parse_payment_result(xml_data)

        # 验证签名
        if result_data['return_code'] == 'SUCCESS' and result_data['result_code'] == 'SUCCESS':
            out_trade_no = result_data['out_trade_no']  # 商户订单号
            transaction_id = result_data['transaction_id']  # 微信支付订单号
            total_fee = result_data['total_fee']  # 订单金额，单位为分
            openid = result_data['openid']  # 用户标识

            # 执行 SQL 更新
            frappe.db.sql("""
                        UPDATE `tabLy Membership Payment`
                       SET `pay_state` = %s,`transaction_id`= %s
                       WHERE `order_number` = %s
                   """, ('已支付',transaction_id, out_trade_no))

            result = frappe.db.sql("""
                        SELECT `parent`
                        FROM `tabLy Membership Payment`
                        WHERE `order_number` = %s
                       """, (out_trade_no,), as_dict=True)

            if result:
				user_id = result[0]['parent']
				# 更新所有用户
				frappe.db.sql("""
				                          UPDATE `tabLy User`
				                          SET `member_level` = %s WHERE `name` = %s
				                      """, ('付费会员',user_id))


            # 提交事务
            frappe.db.commit()

            # 返回成功响应给微信服务器
            return wechat_success_response()
        else:
            # 处理失败的情况
            error_message = result_data.get('return_msg', 'Unknown error')
            frappe.log_error(message=error_message, title="WeChat Pay Notify Error")
            return wechat_fail_response(error_message)
    except WeChatPayException as e:
        frappe.log_error(message=str(e), title="WeChat Pay Exception")
        return wechat_fail_response(str(e))
    except Exception as e:
        frappe.log_error(message=str(e), title="WeChat Pay Notify Exception")
        return wechat_fail_response(str(e))


def get_wechat_pay_client():
    # 微信支付配置
    app_id = 'wx0cdfbdd1a9a07850'
    mch_id = '1694598681'
    api_key = 'aB3dE5fG7hI9jK1LmN0pQrStUvWxYz2B'
    mch_cert = '/etc/wechatpay/apiclient_cert.pem'  # 证书路径
    mch_key = '/etc/wechatpay/apiclient_key.pem'    # 证书密钥路径

    # 初始化 WeChatPay 对象
    wechat_pay = WeChatPay(
        appid=app_id,
        api_key=api_key,
        mch_id=mch_id,
        mch_cert=mch_cert,
        mch_key=mch_key,
        timeout=30
    )
    return wechat_pay


def update_order_status(out_trade_no, transaction_id, total_fee, openid):
    # 根据商户订单号查询订单
    try:
        sales_order = frappe.get_doc('Ly Sales Order', {'order_number': out_trade_no})
    except frappe.DoesNotExistError:
        frappe.log_error(message=f"订单未找到，订单号：{out_trade_no}", title="Order Not Found")
        return

    # 更新订单状态为已支付
    sales_order.status = '已支付'
    sales_order.transaction_id = transaction_id
    sales_order.payment_time = now_datetime()
    sales_order.save(ignore_permissions=True)
    frappe.db.commit()

    # 其他业务逻辑，例如通知用户等
    # ...


def wechat_success_response():
    # 返回给微信服务器的成功响应
    return """
    <xml>
      <return_code><![CDATA[SUCCESS]]></return_code>
      <return_msg><![CDATA[OK]]></return_msg>
    </xml>
    """


def wechat_fail_response(message):
    # 返回给微信服务器的失败响应
    return f"""
    <xml>
      <return_code><![CDATA[FAIL]]></return_code>
      <return_msg><![CDATA[{message}]]></return_msg>
    </xml>
    """
