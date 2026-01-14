
import os

po_file = r"c:\Users\anhhu\New_DermAI\locale\en\LC_MESSAGES\django.po"

new_entries = [
    # Result HTML
    ("Heatmap giải thích", "Heatmap explanation"),
    ("Heatmap hiển thị các vùng ảnh mà AI tập trung để đưa ra dự đoán. Dữ liệu này có thể tham khảo bởi những người có chuyên môn y khoa", "The heatmap highlights areas where AI focused for prediction. This data is for reference by medical professionals."),
    ("Sửa dữ liệu để chẩn đoán nâng cao", "Edit data for advanced diagnosis"),
    ("Sửa thông tin", "Edit information"),
    ("Các thông tin liên quan", "Related information"),
    ("Loại thông tin", "Information type"),
    ("Chi tiết", "Details"),
    ("Giới tính", "Gender"),
    ("Độ tuổi", "Age"),
    ("Triệu chứng", "Symptoms"),
    ("Tiền sử thuốc", "Medication history"),
    ("Tiền sử bệnh", "Medical history"),
    ("Thêm thông tin để chẩn đoán", "Add information for diagnosis"),
    ("Xem hồ sơ", "View Profile"),
    
    # Pharmacy HTML
    ("Nhập địa chỉ/thành phố nếu GPS không hoạt động", "Enter address/city if GPS is unavailable"),
    ("Tìm", "Find"),
    ("Nhà thuốc", "Pharmacy"),
    ("Bệnh viện", "Hospital"),
    ("Phòng khám", "Clinic"),
    ("Nhà thuốc gần đây", "Nearby pharmacies"),
    ("Gợi ý", "Suggestions"),
    ("Cho phép truy cập vị trí khi được hỏi để tìm nhanh nhất.", "Allow location access when asked for fastest search."),
    ("Giới tính bệnh nhân", "Patient Gender"),
    ("Độ tuổi bệnh nhân", "Patient Age"),
    ("Nam", "Male"),
    ("Nữ", "Female"),
    ("Nếu không cho phép, hãy nhập địa chỉ hoặc tên quận / thành phố và nhấn \"Tìm\".", "If denied, enter address or district/city name and press \"Find\"."),
    
    # Disease Names from Image
    ("Mụn cóc", "Warts"),
    ("Da bình thường hoặc cần thêm dữ liệu để chẩn đoán", "Normal skin or additional data needed for diagnosis"),
    ("Bệnh vẩy nến hoặc các bệnh tương tự", "Psoriasis or similar conditions"),
    ("Bệnh ghẻ, bệnh Lyme hoặc các bệnh nhiễm trùng và vết cắn tương tự", "Scabies, Lyme disease, or similar infections and bites"),
    ("Sừng hóa bã nhờn và các khối u lành tính khác", "Seborrheic keratosis and other benign tumors"),
    ("Bệnh chàm", "Eczema"),
    ("Mụn trứng cá, các loại mụn khác hoặc da ửng đỏ", "Acne, other acne types, or skin redness"),
    
    # Home HTML
    ("Upload ảnh để chẩn đoán", "Upload photo for diagnosis"),
    ("Chọn ảnh từ thiết bị của bạn", "Choose photo from your device"),
    ("Upload", "Upload"),
    ("Đóng", "Close"),
    ("Dừng", "Stop"),
    ("Gọi Cấp Cứu", "Call Ambulance"),
    ("Ảnh sẽ được gửi để kiểm tra; nếu server xử lý sẽ chuyển trang kết quả tự động.", "Photo will be sent for inspection; result page will open automatically if server processes it."),
    ("Bạn chưa đăng nhập", "You are not logged in"),
    ("Vui lòng đăng nhập để sử dụng tính năng chụp và gửi ảnh.", "Please login to use capture and send features."),
    ("Đăng nhập", "Login"),
    ("Hủy", "Cancel"),
    ("Upload ảnh", "Upload photo"),
    ("Chụp ảnh", "Capture photo"),
    ("Chụp vùng da để kiểm tra - camera 300×300", "Capture skin area to check - camera 300×300"),
    ("Chuyển camera", "Switch camera"),
    ("Tải ảnh từ thư viện", "Upload from library")
]

with open(po_file, "r", encoding="utf-8") as f:
    content = f.read()

to_append = []
for msgid, msgstr in new_entries:
    if f'msgid "{msgid}"' not in content:
        entry = f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'
        to_append.append(entry)
    else:
        print(f"Skipping existing: {msgid}")

if to_append:
    with open(po_file, "a", encoding="utf-8") as f:
        f.writelines(to_append)
    print(f"Added {len(to_append)} new entries.")
else:
    print("No new entries to add.")
