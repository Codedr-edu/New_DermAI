
import os

files = [
    r"c:\Users\anhhu\New_DermAI\Dermal\templates\home.html",
    r"c:\Users\anhhu\New_DermAI\Dermal\templates\chatbot.html",
    r"c:\Users\anhhu\New_DermAI\Dermal\templates\pharmacy.html",
]

target_strings = [
    "Ảnh sẽ được gửi để kiểm tra",
    "Hỏi bác sĩ ảo",
    "Tìm nhà thuốc gần vị trí"
]

for fpath in files:
    print(f"Checking {os.path.basename(fpath)}...")
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            for target in target_strings:
                if target in line:
                    print(f"Line {i+1}: {repr(line)}")
    except Exception as e:
        print(f"Error reading {fpath}: {e}")
