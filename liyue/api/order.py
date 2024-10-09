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
