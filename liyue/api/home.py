import frappe

@frappe.whitelist(allow_guest=True)
def get_set_list():
	# result = frappe.get_all('Ly Membership Settings',fields=['*'])
	# 获取所有记录的名称
	all_names = frappe.get_all('Ly Homepage Settings', fields=['name'],filters=[["Ly Homepage Settings","enabled","=","1"]])

	# 逐一加载每个文档
	all_docs = []
	for record in all_names:
		doc = frappe.get_doc('Ly Homepage Settings', record.name)
		all_docs.append(doc)

	return all_docs
