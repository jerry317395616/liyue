# Copyright (c) 2024, 1 and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LyHomepageSettings(Document):
	def validate(self):
		if self.enabled:
			# 将其他所有记录的 enabled 字段设置为 False
			frappe.db.sql("""
	                UPDATE `tabLy Homepage Settings`
	                SET enabled = 0
	                WHERE name != %s AND enabled = 1
	            """, self.name)
