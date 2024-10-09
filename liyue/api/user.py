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
        # 获取前端传递的 user_id 和批量地址信息
        user_id = frappe.form_dict.get('user_id')
        addresses = frappe.form_dict.get('addresses')

        if not user_id or not addresses:
            return {"status": "error", "message": "Missing user ID or addresses"}

        # 获取用户文档
        user = frappe.get_doc('Ly User', user_id)
        should_save = False  # 标志变量，是否需要保存

        for address in addresses:
            # 检查是否存在四个字段同时相同的记录
            existing_address = next((
                addr for addr in user.address
                if addr.deceased_person_name == address.get('deceased_person_name') and
                   addr.address == address.get('address') and
                   addr.name_of_deceased_relative == address.get('name_of_deceased_relative') and
                   addr.burial_address == address.get('burial_address')
            ), None)

            if existing_address:
                # 如果找到完全匹配的记录，跳过保存
                frappe.log(
                    f"Skipping address: {address.get('deceased_person_name')}, already exists.")
                continue

            # 如果没有找到匹配的记录，添加一个新记录
            user.append('address', {
                'deceased_person_name': address.get('deceased_person_name'),
                'address': address.get('address'),
                'phone': address.get('phone', ''),  # 如果没有传递 phone 字段，默认设为空
                'name_of_deceased_relative': address.get('name_of_deceased_relative'),
                'relationship': address.get('relationship', ''),  # 如果没有传递 relationship 字段，默认设为空
                'burial_address': address.get('burial_address'),
                'parent': user_id,
                'parentfield': 'address',
                'parenttype': 'Ly User',
                'doctype': 'Ly Address'
            })
            should_save = True  # 标记为需要保存

        # 如果添加了新的地址记录，则保存并提交更改
        if should_save:
            user.save(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "message": "Addresses updated successfully"}
        else:
            return {"status": "success", "message": "No new addresses to add"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_address_batch_error")
        return {"status": "error", "message": str(e)}
