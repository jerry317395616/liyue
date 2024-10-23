import frappe

@frappe.whitelist(allow_guest=True)
def get_order_list():
	# result = frappe.get_all('Ly Membership Settings',fields=['*'])
	# 获取所有记录的名称
	user_id = frappe.form_dict.get('user_id')
	all_names = frappe.get_all('Ly Sales Order', fields=['name'],filters=[["Ly Sales Order","customer","=",user_id]])

	# 初始化用于存储包含图片信息的订单列表
	orders_with_images = []
	# 逐一加载每个文档
	all_docs = []
	# 收集所有的 item_code，用于批量获取图片信息
	item_codes = set()
	for record in all_names:
		doc = frappe.get_doc('Ly Sales Order', record.name)
		all_docs.append(doc)
		# 确保 order_item 是正确的字段名，可能需要根据实际情况调整
		for order_item in doc.order_item:
			# 获取 item_code
			item_code = order_item.item
			item_codes.add(item_code)

	# 批量获取所有 item 的图片信息
	item_images = {}
	if item_codes:
		# 获取所有相关的 Ly Item 文档，只获取 name 和 image 字段
		items = frappe.get_all(
			'Ly Item',
			filters={'name': ['in', list(item_codes)]},
			fields=['name', 'image']
		)
		# 构建 item_code 到 image 的映射
		item_images = {item['name']: item['image'] for item in items}

	# 第二次遍历，构建包含图片信息的订单列表
	for record in all_names:
		order_doc = frappe.get_doc('Ly Sales Order', record.name)
		order_data = order_doc.as_dict()

		# 构建新的 order_item 列表，包含图片信息
		order_items_with_images = []
		for order_item in order_doc.order_item:
			order_item_data = order_item.as_dict()
			item_code = order_item.item
			# 添加图片信息到 order_item_data
			order_item_data['image'] = item_images.get(item_code)
			order_items_with_images.append(order_item_data)

		# 替换订单中的 order_item 列表
		order_data['order_item'] = order_items_with_images
		orders_with_images.append(order_data)

	return orders_with_images

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


@frappe.whitelist(allow_guest=True)  # 设置是否允许游客访问
def get_completed_sales_order(name):
    """
    获取状态为 '已完成' 且名称为指定值的 Ly Sales Order

    :param name: 销售订单的名称
    :return: 查询结果列表
    """
    if not name:
        frappe.throw("参数 'name' 是必需的")

    # 执行 SQL 查询
    query = """
        SELECT * FROM `tabLy Sales Order`
        WHERE status = '已完成' AND name = %s
    """
    results = frappe.db.sql(query, (name,), as_dict=True)
    return results
