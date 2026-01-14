
import os

target_file = r"c:\Users\anhhu\New_DermAI\Dermal\templates\result.html"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Verify content matches expectations before patching
# Line 109 (index 108) should start with the disclaimer
if "*DermAI" not in lines[108]:
    print(f"Warning: Line 109 does not match expected content. Found: {lines[108][:20]}...")
else:
    print("Line 109 verified.")

if "*Nếu bạn" not in lines[110]: # Index 110 is line 111
    print(f"Warning: Line 111 does not match expected content. Found: {lines[110][:20]}...")
else:
    print("Line 111 verified.")

if "Heatmap hiển thị" not in lines[118]: # Index 118 is line 119
    print(f"Warning: Line 119 does not match expected content. Found: {lines[118][:20]}...")
else:
    print("Line 119 verified.")

# Prepare new lines
new_content = []
skip_until = -1

for i, line in enumerate(lines):
    if i < skip_until:
        continue
        
    # Replace lines 109-110 (indices 108, 109)
    if i == 108:
        print("Patching lines 109-110...")
        new_content.append('      <p class="text-danger mb-3">{% trans "*DermAI có thể có những nhầm lẫn trong việc chẩn đoán. Vui lòng tham khảo ý kiến bác sĩ để có chẩn đoán chính xác." %}</p>\n')
        skip_until = 110 # Skip 109
    
    # Replace lines 111-112 (indices 110, 111)
    elif i == 110:
        print("Patching lines 111-112...")
        new_content.append('      <p class="text-danger mb-3">{% trans "*Nếu bạn có chuyên môn y khoa. Hãy kiểm tra thật kĩ tình trạng bệnh nhân bằng các biện pháp y khoa chuẩn. DermAI chỉ có khả năng hỗ trợ tốt nhất trong quá trình tiền chẩn đoán" %}</p>\n')
        skip_until = 112 # Skip 111
    
    # Replace lines 119-120 (indices 118, 119)
    # Check if lines shifted due to previous edits?
    # No, we append to new_content, input `lines` is unchanged.
    elif i == 118:
        print("Patching lines 119-120...")
        new_content.append('      <p class="text-muted small">{% trans "Heatmap hiển thị các vùng ảnh mà AI tập trung để đưa ra dự đoán. Dữ liệu này có thể tham khảo bởi những người có chuyên môn y khoa" %}</p>\n')
        skip_until = 120 # Skip 119
        
    else:
        new_content.append(line)

with open(target_file, "w", encoding="utf-8") as f:
    f.writelines(new_content)
print("Applied deterministic patch.")
