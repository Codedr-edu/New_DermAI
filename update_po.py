
import os

po_file = r"c:\Users\anhhu\Desktop\DermAI - Website\New_DermAI\locale\en\LC_MESSAGES\django.po"

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
    ("Bệnh viện gần đây", "Nearby hospitals"),
    ("Phòng khám gần đây", "Nearby clinics"),
    ("Cơ sở y tế gần đây", "Nearby medical facilities"),
    ("Nhà thuốc gần tôi - DermAI", "Pharmacies near me - DermAI"),
    ("Bệnh viện gần tôi - DermAI", "Hospitals near me - DermAI"),
    ("Phòng khám gần tôi - DermAI", "Clinics near me - DermAI"),
    ("Cơ sở y tế gần tôi - DermAI", "Medical facilities near me - DermAI"),
    ("Tìm nhà thuốc gần vị trí của bạn", "Find pharmacies near your location"),
    ("Tìm bệnh viện gần vị trí của bạn", "Find hospitals near your location"),
    ("Tìm phòng khám gần vị trí của bạn", "Find clinics near your location"),
    ("Tìm cơ sở y tế gần vị trí của bạn", "Find medical facilities near your location"),
    ("Bạn ở đây", "You are here"),
    ("Gợi ý", "Suggestions"),
    ("Cho phép truy cập vị trí khi được hỏi để tìm nhanh nhất.", "Allow location access when asked for fastest search."),
    ("Nếu không cho phép, hãy nhập địa chỉ hoặc tên quận / thành phố và nhấn \"Tìm\".", "If denied, enter address or district/city name and press \"Find\"."),
    ("Không thể xác định vị trí. Hãy nhập địa chỉ thủ công.", "Unable to determine location. Please enter address manually."),
    ("Không tìm thấy địa điểm, thử nhập cụ thể hơn.", "Location not found, try entering more specifically."),
    ("Lỗi khi tìm địa điểm.", "Error finding location."),
    
    # Home HTML
    ("Upload ảnh để chẩn đoán", "Upload photo for diagnosis"),
    ("Chọn ảnh từ thiết bị của bạn", "Choose photo from your device"),
    ("Upload", "Upload"),
    ("Đóng", "Close"),
    ("Dừng", "Stop"),
    ("Mở camera", "Open Camera"),
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
    ("Tải ảnh từ thư viện", "Upload from library"),
    ("Không thể truy cập camera. Vui lòng kiểm tra quyền truy cập hoặc thiết bị.", "Unable to access camera. Please check permissions or device."),
    ("Camera không hoạt động. Vui lòng khởi động lại.", "Camera not working. Please restart."),
    ("Camera chưa sẵn sàng, vui lòng chờ và thử lại.", "Camera not ready, please wait and try again."),
    ("Video chưa tải đầy đủ, vui lòng chờ và thử lại.", "Video not fully loaded, please wait and try again."),
    ("Video không đang phát. Vui lòng thử lại.", "Video not playing. Please try again."),
    ("Lỗi khi xử lý ảnh. Vui lòng thử lại.", "Error processing image. Please try again."),
    
    # Chatbot HTML
    ("Lỗi: Không nhận được phản hồi từ server.", "Error: No response from server."),
    ("Lỗi kết nối:", "Connection error:"),
    
    # General & Error messages
    ("Tên đăng nhập hoặc mật khẩu không chính xác.", "Incorrect username or password."),
    ("Tên đăng nhập đã tồn tại.", "Username already exists."),
    ("Email đã được sử dụng.", "Email is already in use."),
    ("Đã xảy ra lỗi trong quá trình đăng ký: ", "An error occurred during registration: "),
    ("Giới tính bệnh nhân", "Patient Gender"),
    ("Độ tuổi bệnh nhân", "Patient Age"),
    ("Nam", "Male"),
    ("Nữ", "Female"),

    # OAuth
    ("Hoặc đăng nhập với", "Or log in with"),
    ("Hoặc đăng ký với", "Or sign up with"),
    ("Tiếp tục với Google", "Continue with Google"),

    # Social Account Pages
    ("Xác nhận đăng nhập", "Login Confirmation"),
    ("Đăng nhập với Google", "Sign in with Google"),
    ("Bạn đang chuẩn bị đăng nhập vào DermAI bằng tài khoản từ", "You are about to sign in to DermAI using an account from"),
    ("Tiếp tục", "Continue"),
    ("Hủy bỏ", "Cancel"),
    
    ("Lỗi xác thực", "Authentication Error"),
    ("Đã xảy ra lỗi trong quá trình đăng nhập. Vui lòng thử lại sau hoặc sử dụng phương thức khác.", "An error occurred during the login process. Please try again later or use a different method."),
    ("Quay lại Đăng nhập", "Back to Login"),
    ("Trang chủ", "Home"),
    
    ("Hoàn tất đăng ký", "Complete Registration"),
    ("Hoàn tất tài khoản", "Complete Account Setup"),
    ("Bạn đã xác thực thành công qua", "You have successfully authenticated via"),
    ("Vui lòng xác nhận tên đăng nhập của bạn để hoàn tất.", "Please confirm your username to complete."),
    ("Nhập tên đăng nhập", "Enter username"),
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
