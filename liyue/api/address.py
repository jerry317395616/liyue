# import frappe
#
#
# @frappe.whitelist(allow_guest=True)
# def get_address():
# 	query = """
# 			select * from `tabLy Address` where deceased_person_name = %(deceased_person_name)s and
# 			name_of_deceased_relative = %(name_of_deceased_relative)s
# 		"""
# 	deceased_person_name = frappe.form_dict.get('deceased_person_name')
# 	name_of_deceased_relative = frappe.form_dict.get('name_of_deceased_relative')
# 	address = frappe.form_dict.get('address')
# 	burial_address = frappe.form_dict.get('burial_address')
#
# 	user_id = frappe.form_dict.get('user_id')
# 	# 执行查询
# 	result = frappe.db.sql(query, {"deceased_person_name": deceased_person_name,"name_of_deceased_relative":name_of_deceased_relative}, as_dict=True)
# 	if not result:
# 		# 创建新文档
# 		new_address = frappe.get_doc({
# 			"doctype": "Ly Address",
# 			"name": "",  # Frappe 会自动生成名称
# 			"deceased_person_name": deceased_person_name,
# 			"address": address,
# 			"name_of_deceased_relative": name_of_deceased_relative,
# 			"burial_address": burial_address,
# 			"parent": user_id,
# 			"parenttype": "Ly User",
# 			"parentfield": "address",
# 			"docstatus": 0,
# 			"idx": 1,
# 			"is_default": 0,
# 			"owner": "Administrator",
# 			"modified_by": "Administrator"
# 		})
# 		# 插入文档
# 		new_address.insert()
#
# 		# 提交事务（如果在需要时）
# 		frappe.db.commit()
# 		return "没有"
# 	return result
# custom_api_app/custom_api_app/api.py

import frappe
import json
from frappe import _

@frappe.whitelist(allow_guest=True)
def save_addresses(user_id, addresses):
    """
    批量保存地址信息

    :param user_id: 用户 ID
    :param addresses: 地址列表（JSON 字符串）
    :return: 成功插入的地址名称列表
    """
    try:
        # 参数验证
        if not user_id:
            frappe.throw(_("参数 'user_id' 是必需的"))
        if not addresses:
            frappe.throw(_("参数 'addresses' 是必需的"))

        # 如果 'addresses' 是字符串，尝试解析为 JSON
        if isinstance(addresses, str):
            try:
                addresses = json.loads(addresses)
            except json.JSONDecodeError:
                frappe.throw(_("参数 'addresses' 必须是有效的 JSON 格式"))
        elif not isinstance(addresses, list):
            frappe.throw(_("参数 'addresses' 必须是一个列表"))

        # 检查用户是否存在
        try:
            user = frappe.get_doc("Ly User", user_id)
        except frappe.DoesNotExistError:
            frappe.throw(_("用户未找到: {0}").format(user_id))



        # 初始化返回列表
        inserted_addresses = []

        for addr in addresses:
            deceased_person_name = addr.get('deceased_person_name')
            name_of_deceased_relative = addr.get('name_of_deceased_relative')
            address = addr.get('address')
            burial_address = addr.get('burial_address')

            # 验证每个地址的必要字段
            required_fields = ['deceased_person_name', 'address', 'name_of_deceased_relative', 'burial_address']
            missing_fields = [field for field in required_fields if not addr.get(field)]
            if missing_fields:
                frappe.throw(_("地址信息中缺少字段: {0}").format(", ".join(missing_fields)))

            # 检查地址是否已存在
            query = """
                SELECT name FROM `tabLy Address`
                WHERE deceased_person_name = %(deceased_person_name)s
                AND name_of_deceased_relative = %(name_of_deceased_relative)s
            """
            result = frappe.db.sql(query, {
                "deceased_person_name": deceased_person_name,
                "name_of_deceased_relative": name_of_deceased_relative
            }, as_dict=True)

            if not result:
                # 创建新文档
                new_address = frappe.get_doc({
                    "doctype": "Ly Address",
                    "deceased_person_name": deceased_person_name,
                    "address": address,
                    "name_of_deceased_relative": name_of_deceased_relative,
                    "burial_address": burial_address,
                    "parent": user_id,
                    "parenttype": "Ly User",
                    "parentfield": "address",
                    "docstatus": 0,
                    "idx": 1,  # 根据实际需求设置
                    "is_default": 0,
                    # "owner": frappe.session.user,  # Frappe 会自动处理
                    # "modified_by": frappe.session.user  # Frappe 会自动处理
                })
                # 插入文档
                new_address.insert()
                inserted_addresses.append(new_address.name)

        # 提交事务
        frappe.db.commit()

        return {"inserted": inserted_addresses}

    except frappe.ValidationError as ve:
        # 已知的验证错误
        frappe.log_error(message=str(ve), title="Save Addresses Validation Error")
        frappe.throw(ve)
    except Exception as e:
        # 未知错误
        frappe.log_error(message=str(e), title="Save Addresses Failed")
        frappe.throw(_("保存地址信息失败: {0}").format(str(e)))

@frappe.whitelist(allow_guest=True)
def get_addresses(user_id):

	# 检查地址是否已存在
	query = """
	               SELECT * FROM `tabLy Address`
	               WHERE parent = %(parent)s
	           """
	result = frappe.db.sql(query, {
		"parent": user_id,
	}, as_dict=True)
	return result
