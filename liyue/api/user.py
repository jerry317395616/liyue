import frappe

@frappe.whitelist(allow_guest=True)
def get_user_list():
	id = frappe.form_dict.get('id')
	user = frappe.get_doc('Ly User',id)
	return user

# 新增积分
@frappe.whitelist(allow_guest=True)
def add_points_record(user_id, points):
	# 获取 Ly User 文档
	user = frappe.get_doc('Ly User', user_id)

	# 新增一个 points_records 行
	user.append('points_records', {
		'points': points,
		# 其他子表字段，可以根据 Doctype 定义进行添加
	})

	# 保存主文档
	user.save()

	return {"status": "success", "message": "Points record added successfully"}

# 保存祭祀信息
@frappe.whitelist(allow_guest=True)
def save_address():
	try:
		# 获取前端发送的数据
		user_id = frappe.form_dict.get('user_id')
		addresses = frappe.form_dict.get('addresses')

		if not user_id or not addresses:
			return {"status": "error", "message": "Missing user ID or addresses"}

		# 获取用户文档
		user = frappe.get_doc('Ly User', user_id)

		# 先清除现有的 address 子表
		user.set('address', [])

		# 批量插入新地址数据
		for address in addresses:
			user.append('address', {
				'deceased_person_name': address.get('deceased_person_name'),
				'address': address.get('address'),
				'phone': address.get('phone'),  # 确保前端传递了 phone 字段
				'name_of_deceased_relative': address.get('name_of_deceased_relative'),
				'relationship': address.get('relationship'),
				'burial_address': address.get('burial_address'),
				'parent': user_id,
				'parentfield': 'address',
				'parenttype': 'Ly User',
				'doctype': 'Ly Address',
			})

		# 保存主表和子表
		user.save()
		frappe.db.commit()

		return {"status": "success", "message": "Addresses updated successfully"}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "update_address_batch_error")
		return {"status": "error", "message": str(e)}
