# apps/membership_app/membership_app/api.py

import frappe
from frappe import _
from frappe.utils.response import build_response
import os
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def download_image(sales_order,image_type):
    file_found = False

    image_filename = image_type+".jpg"
    # 动态构建图片路径
    image_path = os.path.join(
        frappe.get_app_path('liyue'),  # 确保应用名称正确
        'public',
        'images',
        image_filename
    )
    if os.path.exists(image_path):
        file_found = True

    if not file_found:
        frappe.throw(_("Image not found: {0}").format(image_path), frappe.DoesNotExistError)

    # 读取并处理图片内容
    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)

            # 设置要添加的文字
            # 支持通过参数传递文字内容
            # 默认文字为 "默认文字"
            text = "a"
            text2 = "b"
            text3 = "c"
            text4 = "d"

            # 使用系统默认字体
            try:
                font_path = os.path.join(
					frappe.get_app_path('liyue'),  # 确保字体路径正确
					'public',
					'fonts',
					'arial.ttf'  # 替换为实际的字体文件
                )
                # font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # 修改为实际存在的字体路径
                font = ImageFont.truetype(font_path, int(100))
                # font = ImageFont.load_default()
            except Exception as e:
                frappe.throw(_("Failed to load default font: {0}").format(str(e)))

            # 设置文字颜色
            text_color = (255, 0, 0)  # 红色，您可以根据需要更改

            # 动态设置位置，确保传入的 x 和 y 是整数
            try:
                position = (int(1150), int(250))
                position2 = (int(1150), int(350))
                position3 = (int(1150), int(450))
                position4 = (int(1050), int(350))
            except ValueError:
                frappe.throw(_("Invalid position coordinates: x={0}, y={1}").format(50, 50))

            # 执行 SQL 查询
            result = frappe.db.sql("""
            SELECT deceased_person_name AS name, address,count
			FROM `tabLy Form Generation`
			WHERE parent = %s
			LIMIT 1
			""", (sales_order), as_dict=True)

            # 处理结果
            if result:
                name = result[0].name
                address = result[0].address
                char_list1 = list(address)
                name_list = list(name)
                text = char_list1[0]
                text2 = char_list1[1]
                text3 = char_list1[2]
                count = result[0].count
            # 初始化起始坐标
            x = 1150
            y = 250
            for char in char_list1:
                position = (int(x), int(y))
                # 添加文字到图片
                draw.text(position, char, font=font, fill=text_color)
                y+=100
            # 添加文字到图片
            # draw.text(position, text, font=font, fill=text_color)
            # draw.text(position2, text2, font=font, fill=text_color)
            # draw.text(position3, text3, font=font, fill=text_color)
            # draw.text(position4, text4, font=font, fill=text_color)
            x1 = 1050
            y1 = 250
            for name in name_list:
                position = (int(x1), int(y1))
                # 添加文字到图片
                draw.text(position, name, font=font, fill=text_color)
                y1 += 100

            count_position = (int(230), int(350))
            draw.text(count_position, str(count), font=font, fill=text_color)

            if image_type == '3':

                result1 = frappe.db.sql("""
			         select item.item_name,toi.quantity from `tabLy Sales Order` tso
			         left join `tabLy Order Item` toi on toi.parent = tso.name
			            left join `tabLy Item` item on item.name = toi.item
			         where tso.name= %s and item.item_name = '金元宝'
			            	           	            """, (sales_order), as_dict=True)

                count1 = result1[0].quantity
                count_position1 = (int(900), int(350))
                draw.text(count_position1, str(count1), font=font, fill=text_color)


            now = datetime.now()
            year = now.year
            month = now.month
            day = now.day
            year_position = (int(10), int(150))
            draw.text(year_position, str(year), font=font, fill=text_color)
            month_position = (int(50), int(350))
            draw.text(month_position, str(month), font=font, fill=text_color)
            day_position = (int(50), int(500))
            draw.text(day_position, str(day), font=font, fill=text_color)


            # 将修改后的图片保存到内存中
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format=img.format)
            img_content = img_byte_arr.getvalue()

            # 构建下载响应
            frappe.local.response.filename = image_filename
            frappe.local.response.filecontent = img_content
            frappe.local.response.type = "download"
            frappe.local.response.filetype = "image/jpeg"
            return build_response()
    except Exception as e:
        frappe.log_error(message=str(e), title="Error processing image file")
        frappe.throw(_("Error processing image: {0}").format(str(e)), frappe.DoesNotExistError)
