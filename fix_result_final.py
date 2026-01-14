
import os

target_file = r"c:\Users\anhhu\New_DermAI\Dermal\templates\result.html"

# Define the clean blocks to replace the broken/split ones
replacements = [
    (
        "Heatmap hiển thị các vùng ảnh mà AI tập trung", 
        '      <p class="text-muted small">{% trans "Heatmap hiển thị các vùng ảnh mà AI tập trung để đưa ra dự đoán. Dữ liệu này có thể tham khảo bởi những người có chuyên môn y khoa" %}</p>'
    ),
    (
        "*DermAI có thể có những nhầm lẫn",
        '      <p class="text-danger mb-3">{% trans "*DermAI có thể có những nhầm lẫn trong việc chẩn đoán. Vui lòng tham khảo ý kiến bác sĩ để có chẩn đoán chính xác." %}</p>'
    ),
    (
        "*Nếu bạn có chuyên môn y khoa",
        '      <p class="text-danger mb-3">{% trans "*Nếu bạn có chuyên môn y khoa. Hãy kiểm tra thật kĩ tình trạng bệnh nhân bằng các biện pháp y khoa chuẩn. DermAI chỉ có khả năng hỗ trợ tốt nhất trong quá trình tiền chẩn đoán" %}</p>'
    ),
]

try:
    with open(target_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    skip_until_tag_closure = False
    
    for i, line in enumerate(lines):
        if skip_until_tag_closure:
            # We are skipping garbage lines from a previous split tag
            if "%}" in line:
                skip_until_tag_closure = False
            continue
            
        matched = False
        for search_key, clean_line in replacements:
            if search_key in line:
                print(f"Replacing broken block at line {i+1}: {search_key[:20]}...")
                new_lines.append(clean_line + "\n")
                matched = True
                
                # Check if this was a split tag start
                # If the line doesn't end with "%}</p>" or "%}", we might need to skip next lines
                stripped = line.strip()
                if not ("%}" in line and stripped.endswith("</p>") or stripped.endswith("%}")):
                     # It matches the search key but looks cut off?
                     # Actually, my fuzzy match just finds the start.
                     # If the ORIGINAL line was split, the rest is on next lines.
                     # I need to skip the next lines until we find the end of the paragraph or tag.
                     # Heuristic: if next line starts with text or %}, skip it.
                     pass 
                
                # Simpler heuristic: If replacing a known split block, look ahead
                if "Heatmap hiển thị" in search_key or "*DermAI" in search_key or "*Nếu bạn" in search_key:
                     # Check next few lines
                     lookahead = 1
                     while i + lookahead < len(lines):
                         next_l = lines[i+lookahead].strip()
                         # If it looks like garbage continuation
                         if next_l.startswith("có thể tham khảo") or next_l.startswith("kiến bác sĩ") or next_l.startswith("bằng các biện pháp"):
                             print(f"  Skipping garbage line {i+1+lookahead}")
                             skip_until_tag_closure = False # handled by loop logic? No, need to manually skip
                             # We can't change loop iterator. We set a flag or just consume?
                             # I'll just not append them.
                             # But I'm iterating. I can't skip ahead easily in 'for'.
                             # Rewriting structure to `while` or use an ignore_indices set.
                             pass
                         elif next_l.endswith("%}</p>"):
                             print(f"  Skipping closing garbage line {i+1+lookahead}")
                             # This is the end.
                             # But I can't signal the outer loop to skip.
                             # I'll restart the script with a while loop structure.
                             raise ValueError("Need while loop")
                         else:
                             break
                         lookahead += 1
                break
        
        if not matched:
            new_lines.append(line)

except ValueError:
    # Retry with while loop logic
    print("Retrying with while loop logic...")
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        matched = False
        for search_key, clean_line in replacements:
            if search_key in line:
                print(f"Replacing broken block at line {i+1}")
                new_lines.append(clean_line + "\n")
                matched = True
                
                # Consume garbage lines
                j = 1
                while i + j < len(lines):
                    next_l = lines[i+j].strip()
                    # Identify specific garbage signatures based on known split content
                    if (search_key.startswith("Heatmap") and (next_l.startswith("có thể tham khảo") or next_l.startswith("tham khảo bởi") or "%}" in next_l)) or \
                       (search_key.startswith("*DermAI") and (next_l.startswith("kiến bác sĩ") or next_l.startswith("để có chẩn") or "%}" in next_l)) or \
                       (search_key.startswith("*Nếu bạn") and (next_l.startswith("bằng các biện") or next_l.startswith("hỗ trợ tốt") or "%}" in next_l)):
                        print(f"  Skipping garbage at {i+1+j}: {next_l}")
                        j += 1
                    else:
                        break
                i += j - 1
                break
        
        if not matched:
            new_lines.append(line)
        i += 1

    with open(target_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Saved clean file.")
