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
	user_id = frappe.form_dict.get('user_id')
	deceased_person_name = frappe.form_dict.get('deceased_person_name')
	address = frappe.form_dict.get('address')
	phone = frappe.form_dict.get('phone')
	name_of_deceased_relative = frappe.form_dict.get('name_of_deceased_relative')
	relationship = frappe.form_dict.get('relationship')
	burial_address = frappe.form_dict.get('burial_address')
	user = frappe.get_doc('Ly User', user_id)
	user.append('address', {
		'deceased_person_name': deceased_person_name,
		'address': address,
		'phone': phone,
		'name_of_deceased_relative': name_of_deceased_relative,
		'relationship': relationship,
		'burial_address': burial_address,
		"parent": user_id,
		"parentfield": "address",
		"parenttype": "Ly User",
		"doctype": "Ly Address"
	})
	# 保存主文档
	user.save()
	return {"status": "success", "message": "address added successfully"}
