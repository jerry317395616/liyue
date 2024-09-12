# Copyright (c) 2024, 1 and contributors
# For license information, please see license.txt
import random
import string
import frappe
from frappe.model.document import Document


class LyReferral(Document):
	def before_insert(self):
		# 自动生成引荐码
		self.referral_code = self.generate_unique_referral_code()

	def generate_unique_referral_code(self, length=8):
		# 定义引荐码长度（默认为8位）
		while True:
			# 生成随机引荐码，包含字母和数字
			referral_code = ''.join(
				random.choices(string.ascii_uppercase + string.digits, k=length))

			# 检查引荐码是否唯一，防止重复
			if not frappe.db.exists('Ly Referral', {'referral_code': referral_code}):
				return referral_code
