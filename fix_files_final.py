
import os

replacements = {
    r"c:\Users\anhhu\New_DermAI\Dermal\templates\home.html": {
        "search": "Ảnh sẽ được gửi",
        "replace": '            <div class="mt-3 hint">{% trans "Ảnh sẽ được gửi để kiểm tra; nếu server xử lý sẽ chuyển trang kết quả tự động." %}</div>\n'
    },
    r"c:\Users\anhhu\New_DermAI\Dermal\templates\chatbot.html": {
        "search": "Hỏi bác sĩ ảo",
        "replace": '                    <div class="hint" style="font-size:0.85rem;color:#6b7280;">{% trans "Hỏi bác sĩ ảo powered by Gemini" %}</div>\n'
    },
    r"c:\Users\anhhu\New_DermAI\Dermal\templates\pharmacy.html": {
        "search": "Tìm nhà thuốc gần vị trí",
        "replace": '                <div class="hint text-muted d-none d-md-block" id="mainHint">{% trans "Tìm nhà thuốc gần vị trí của bạn" %}</div>\n'
    }
}

for fpath, data in replacements.items():
    print(f"Fixing {os.path.basename(fpath)}...")
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        replaced = False
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
            if data["search"] in line:
                print(f"  Found broken line at {i+1}")
                new_lines.append(data["replace"])
                replaced = True
                # Check if it was split and the next line was part of it
                # If the line ends with common split chars or looks incomplete, we effectively merging.
                # But here we assume the search phrase identifies the start. 
                # If the tag was split, the closing ' %}' might be on next line.
                # We should inspect next line to see if it's jst the closing tag.
                if i + 1 < len(lines):
                    next_l = lines[i+1].strip()
                    if next_l.startswith("%}") or next_l.startswith("động.' %}") or next_l.startswith("Gemini' %}") or next_l == "%}</div>":
                        print(f"  Skipping fragmentation on line {i+2}")
                        skip_next = True
            else:
                new_lines.append(line)
        
        if replaced:
            with open(fpath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print("  Saved.")
        else:
            print("  Target not found!")

    except Exception as e:
        print(f"Error fixing {fpath}: {e}")
