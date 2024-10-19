import frappe

@frappe.whitelist(allow_guest=True)
def get_order_list():
	# result = frappe.get_all('Ly Membership Settings',fields=['*'])
	# 获取所有记录的名称
	user_id = frappe.form_dict.get('user_id')
	all_names = frappe.get_all('Ly Sales Order', fields=['name'],filters=[["Ly Sales Order","customer","=",user_id]])

	# 逐一加载每个文档
	all_docs = []
	for record in all_names:
		doc = frappe.get_doc('Ly Sales Order', record.name)
		all_docs.append(doc)

	return all_docs


@frappe.whitelist(allow_guest=True)
def cancel_order():
	"""
	删除指定用户的销售订单
	"""
	user_id = frappe.form_dict.get('user_id')
	order_id = frappe.form_dict.get('order_id')

	if not user_id:
		frappe.throw("Missing 'user_id' parameter", frappe.MissingArgumentError)

	if not order_id:
		frappe.throw("Missing 'order_id' parameter", frappe.MissingArgumentError)

	try:
		# 获取订单文档
		order = frappe.get_doc('Ly Sales Order', order_id)

		# 检查订单是否属于该用户
		if order.customer != user_id:
			frappe.throw("You are not authorized to delete this order", frappe.PermissionError)

		# 检查订单状态，只有特定状态的订单可以删除（根据实际业务需求调整）
		if order.status not in ['待支付', '已取消']:
			frappe.throw("Only orders with status '待支付' or '已取消' can be deleted",
						 frappe.ValidationError)

		# 如果订单已经是 'Cancelled'，无需重复操作
		if order.status == '已取消':
			return {
				'success': False,
				'message': 'The order is already cancelled.'
			}
		order.status = '已取消'
		order.save()

		return {
			'success': True,
			'message': 'Order has been successfully deleted.'
		}

	except frappe.DoesNotExistError:
		frappe.throw("Order with ID {0} does not exist".format(order_id),
					 frappe.DoesNotExistError)
	except frappe.PermissionError as e:
		frappe.throw(e.message, frappe.PermissionError)
	except frappe.ValidationError as e:
		frappe.throw(e.message, frappe.ValidationError)
	except Exception as e:
		frappe.log_error(message=str(e), title="Delete Order Error")
		frappe.throw("An unexpected error occurred while deleting the order.",
					 frappe.ValidationError)


@frappe.whitelist(allow_guest=True)
def get_order_detail():
    """
    获取指定订单的详细信息
    """
    user_id = frappe.form_dict.get('user_id')
    order_id = frappe.form_dict.get('order_id')

    if not user_id:
        frappe.throw("Missing 'user_id' parameter", frappe.MissingArgumentError)

    if not order_id:
        frappe.throw("Missing 'order_id' parameter", frappe.MissingArgumentError)

    try:
        # 获取订单文档
        order = frappe.get_doc('Ly Sales Order', order_id)

        # 检查订单是否属于该用户
        if order.customer != user_id:
            frappe.throw("You are not authorized to view this order", frappe.PermissionError)

        # 构建订单详细信息
        order_details = order


        return {
            'success': True,
            'message': order_details
        }

    except frappe.DoesNotExistError:
        frappe.throw("Order with ID {0} does not exist".format(order_id),
                     frappe.DoesNotExistError)
    except frappe.PermissionError as e:
        frappe.throw(str(e), frappe.PermissionError)
    except Exception as e:
        frappe.log_error(message=str(e), title="Get Order Detail Error")
        frappe.throw("An unexpected error occurred while retrieving the order details.",
                     frappe.ValidationError)
