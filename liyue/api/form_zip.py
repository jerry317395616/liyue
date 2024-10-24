import frappe
from frappe import _
from frappe.utils.response import build_response
import os
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

def get_image_data(sales_order, image_type):
    """
    根据销售订单名称和图片类型获取图片的二进制数据，并在图片上添加文本。
    """
    # 动态构建图片文件名和路径
    image_filename = f"{image_type}.jpg"  # 使用 PNG 格式，与前端一致
    image_path = os.path.join(
        frappe.get_app_path('liyue'),  # 确保应用名称正确
        'public',
        'images',
        image_filename
    )

    if not os.path.exists(image_path):
        return None

    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)

            # 执行 SQL 查询获取文本内容
            result = frappe.db.sql("""
                SELECT deceased_person_name AS name, address,count
                FROM `tabLy Form Generation`
                WHERE parent = %s
                LIMIT 1
            """, (sales_order), as_dict=True)

            if result:
                name = result[0].name
                address = result[0].address
                char_list1 = list(address)
                name_list = list(name)
                count = result[0].count
            else:
                char_list1 = []
                name_list = []

            # 使用系统字体
            try:
                font_path = os.path.join(
                    frappe.get_app_path('liyue'),  # 确保字体路径正确
                    'public',
                    'fonts',
                    'arial.ttf'  # 替换为实际的字体文件
                )
                font = ImageFont.truetype(font_path, size=100)  # 调整字体大小
            except Exception as e:
                frappe.throw(_("Failed to load font: {0}").format(str(e)))

            # 设置文字颜色
            text_color = (255, 0, 0)  # 红色

            # 添加地址字符，每个字符垂直排列
            x = 1150
            y = 250
            for char in char_list1:
                position = (x, y)
                draw.text(position, char, font=font, fill=text_color)
                y += 100

            # 添加名字字符，每个字符垂直排列
            x1 = 1050
            y1 = 250
            for name_char in name_list:
                position = (x1, y1)
                draw.text(position, name_char, font=font, fill=text_color)
                y1 += 100

            count_position = (int(230), int(350))
            draw.text(count_position, str(count), font=font, fill=text_color)
            # if image_type == '3':
            #     result1 = frappe.db.sql("""
            # 			         select item.item_name,toi.quantity from `tabLy Sales Order` tso
            # 			         left join `tabLy Order Item` toi on toi.parent = tso.name
            # 			            left join `tabLy Item` item on item.name = toi.item
            # 			         where tso.name= %s and item.item_name = '金元宝'
            # 			            	           	            """, (sales_order),
			# 							as_dict=True)
			#
            #     count1 = result1[0].quantity
            #     count_position1 = (int(900), int(350))
            #     draw.text(count_position1, str(count1), font=font, fill=text_color)

            # now = datetime.now()
            # year = now.year
            # month = now.month
            # day = now.day
            # year_position = (int(10), int(150))
            # draw.text(year_position, str(year), font=font, fill=text_color)
            # month_position = (int(50), int(350))
            # draw.text(month_position, str(month), font=font, fill=text_color)
            # day_position = (int(50), int(500))
            # draw.text(day_position, str(day), font=font, fill=text_color)

            # 将修改后的图片保存到内存中
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')  # 明确指定保存格式为 PNG
            img_content = img_byte_arr.getvalue()

            return img_content
    except Exception as e:
        frappe.log_error(message=str(e), title="Error processing image file")
        return None

@frappe.whitelist(allow_guest=True)
def download_image(sales_order, image_type):
    """
    下载单个图片，添加文本后返回
    """
    img_content = get_image_data(sales_order, image_type)

    if not img_content:
        frappe.throw(_("Image not found or failed to process: type {0}").format(image_type), frappe.DoesNotExistError)

    # 构建下载响应
    filename = f"{image_type}.jpg"
    frappe.local.response.filename = filename
    frappe.local.response.filecontent = img_content
    frappe.local.response.type = "download"
    frappe.local.response.filetype = "image/png"
    return build_response()

@frappe.whitelist()
def download_images_zip(sales_order):
    """
    下载三个图片，打包成 ZIP 文件并返回
    """
    image_types = ['1', '2', '3']  # 根据实际情况修改

    # 创建一个内存中的 ZIP 文件
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for img_type in image_types:
            img_content = get_image_data(sales_order, img_type)
            if img_content:
                filename = f"Ly_Sales_Order_{sales_order}_{img_type}.png"
                zip_file.writestr(filename, img_content)
            else:
                frappe.log_error(message=f"Image type {img_type} not found or failed to process.", title="Image Download Error")

    zip_buffer.seek(0)
    zip_content = zip_buffer.getvalue()

    # 构建下载响应
    frappe.local.response.filename = f"Ly_Sales_Order_{sales_order}.zip"
    frappe.local.response.filecontent = zip_content
    frappe.local.response.type = "download"
    frappe.local.response.filetype = "application/zip"
    return build_response()
