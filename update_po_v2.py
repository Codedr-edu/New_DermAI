
import os

po_file = r"c:\Users\anhhu\New_DermAI\locale\en\LC_MESSAGES\django.po"

new_entries = [
    ("*DermAI có thể có những nhầm lẫn trong việc chẩn đoán. Vui lòng tham khảo ý kiến bác sĩ để có chẩn đoán chính xác.", 
     "*DermAI may make mistakes in diagnosis. Please consult a doctor for an accurate diagnosis."),
    ("*Nếu bạn có chuyên môn y khoa. Hãy kiểm tra thật kĩ tình trạng bệnh nhân bằng các biện pháp y khoa chuẩn. DermAI chỉ có khả năng hỗ trợ tốt nhất trong quá trình tiền chẩn đoán", 
     "*If you have medical expertise, please strictly check the patient's condition using standard medical measures. DermAI is only capable of best supporting the pre-diagnosis process.")
]

with open(po_file, "r", encoding="utf-8") as f:
    content = f.read()

to_append = []
for msgid, msgstr in new_entries:
    if f'msgid "{msgid}"' not in content:
        entry = f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'
        to_append.append(entry)
    else:
        print(f"Skipping existing: {msgid[:20]}...")

if to_append:
    with open(po_file, "a", encoding="utf-8") as f:
        f.writelines(to_append)
    print(f"Added {len(to_append)} new entries.")
else:
    print("No new entries to add.")
