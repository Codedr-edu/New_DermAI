
import os

replacements = {
    r"c:\Users\anhhu\New_DermAI\Dermal\templates\pharmacy.html": [
        {
            "search": "Tìm nhà thuốc gần vị trí của bạn",
            "replace": '                <div class="hint text-muted d-none d-md-block" id="mainHint">{% trans "Tìm nhà thuốc gần vị trí của bạn" %}</div>\n',
            "is_split": True
        },
        {
            "search": "Nếu không cho phép, hãy nhập địa chỉ",
            "replace": '                                <li>{% trans \'Nếu không cho phép, hãy nhập địa chỉ hoặc tên quận / thành phố và nhấn "Tìm".\' %}</li>\n',
            "is_split": True
        }
    ],
    r"c:\Users\anhhu\New_DermAI\Dermal\templates\result.html": [
        {
            "search": "Heatmap hiển thị các vùng ảnh",
            "replace": '      <p class="text-muted small">{% trans "Heatmap hiển thị các vùng ảnh mà AI tập trung để đưa ra dự đoán. Dữ liệu này có thể tham khảo bởi những người có chuyên môn y khoa" %}</p>\n',
            "is_split": True
        },
        {
            "search": "*DermAI có thể có những nhầm lẫn",
            "replace": '      <p class="text-danger mb-3">{% trans "*DermAI có thể có những nhầm lẫn trong việc chẩn đoán. Vui lòng tham khảo ý kiến bác sĩ để có chẩn đoán chính xác." %}</p>\n',
            "is_split": True
        },
        {
            "search": "*Nếu bạn có chuyên môn y khoa",
            "replace": '      <p class="text-danger mb-3">{% trans "*Nếu bạn có chuyên môn y khoa. Hãy kiểm tra thật kĩ tình trạng bệnh nhân bằng các biện pháp y khoa chuẩn. DermAI chỉ có khả năng hỗ trợ tốt nhất trong quá trình tiền chẩn đoán" %}</p>\n',
            "is_split": True
        }
    ],
    r"c:\Users\anhhu\New_DermAI\Dermal\templates\profile.html": [
        {
            "search": "classification.uploaded_at",
            "replace": '                        <small class="text-muted">{% trans "Ngày tải lên" %}: {{ classification.uploaded_at|date:"d/m/Y H:i" }}</small>\n',
            "is_split": True
        }
    ]
}

for fpath, fixes in replacements.items():
    print(f"Fixing {os.path.basename(fpath)}...")
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        skip_count = 0
        
        for i, line in enumerate(lines):
            if skip_count > 0:
                skip_count -= 1
                continue
            
            matched = False
            for fix in fixes:
                if fix["search"] in line:
                    print(f"  Found target '{fix['search']}' at line {i+1}")
                    new_lines.append(fix["replace"])
                    matched = True
                    # Heuristic to skip garbage lines if split
                    # check next few lines for closing characters
                    if fix.get("is_split"):
                        # Peek ahead
                        lookahead = 1
                        while i + lookahead < len(lines):
                            next_l = lines[i+lookahead].strip()
                            # If next line looks like a continuation or closing tag
                            if next_l.startswith("%}") or next_l.startswith("pháp y khoa chuẩn") or next_l.startswith("sĩ để có") or next_l.startswith("H:i") or next_l == "}}" or next_l == "}}</small>" or next_l.startswith("\"Tìm\""):
                                print(f"    Skipping split fragment at {i+1+lookahead}: {next_l}")
                                skip_count += 1
                                lookahead += 1
                            else:
                                break
                    break
            
            if not matched:
                new_lines.append(line)
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("  Saved.")

    except Exception as e:
        print(f"Error fixing {fpath}: {e}")
