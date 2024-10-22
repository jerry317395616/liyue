// // Frappe 前端脚本
// frappe.ui.form.on("Ly Sales Order", {
//     refresh(frm) {
//         frm.add_custom_button('打印表文', () => {
//             // 获取当前文档的 name 作为参数
//             const sales_order_name = frm.doc.name;
//
//             if (!sales_order_name) {
//                 frappe.msgprint(__('当前文档没有名称，无法下载图片。'));
//                 return;
//             }
//
//             // 定义需要下载的图片类型或标识符
//             const imageTypes = ['1', '2', '3']; // 根据实际情况修改
//
//             imageTypes.forEach((type) => {
//                 // 构建每个图片的下载 URL
//                 const download_url = `/api/method/liyue.api.form.download_image?sales_order=${encodeURIComponent(sales_order_name)}&image_type=${type}`;
//
//                 // 创建一个隐藏的 <a> 元素并触发点击下载
//                 const link = document.createElement('a');
//                 link.href = download_url;
//                 link.download = `Ly_Sales_Order_${sales_order_name}_${type}.png`; // 设置下载的文件名
//                 document.body.appendChild(link);
//                 link.click();
//                 document.body.removeChild(link);
//             });
//         });
//     },
// });
// Frappe 前端脚本
frappe.ui.form.on("Ly Sales Order", {
    refresh(frm) {
        frm.add_custom_button('打印表文', () => {
            // 获取当前文档的 name 作为参数
            const sales_order_name = frm.doc.name;

            if (!sales_order_name) {
                frappe.msgprint(__('当前文档没有名称，无法下载图片。'));
                return;
            }

            // 构建下载 URL
            const download_url = `/api/method/liyue.api.form_zip.download_images_zip?sales_order=${encodeURIComponent(sales_order_name)}`;

            // 创建一个隐藏的 <a> 元素并触发点击下载
            const link = document.createElement('a');
            link.href = download_url;
            link.download = `Ly_Sales_Order_${sales_order_name}.zip`; // 设置下载的文件名
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    },
});

