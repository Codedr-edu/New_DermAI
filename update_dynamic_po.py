
import os

po_file = r"c:\Users\anhhu\New_DermAI\locale\en\LC_MESSAGES\django.po"

new_entries = [
    # Gender
    ("Nam", "Male"),
    ("Nữ", "Female"),
    
    # Disease names
    ("Mụn trứng cá", "Acne"),
    ("Bệnh vẩy nến", "Psoriasis"),
    ("Bệnh chàm", "Eczema"),
    ("Hắc lào", "Ringworm"),
    ("Lang ben", "Tinea versicolor"),
    ("Mụn cóc", "Warts"),
    ("Ung thư da", "Skin cancer"),
    ("Bớt", "Nevus"),
    ("Viêm da cơ địa", "Atopic dermatitis"),
    ("Thủy đậu", "Chickenpox"),
    ("Zona", "Shingles"),
    ("Da bình thường", "Normal skin"),
    ("Dị ứng", "Allergy"),
    ("Ghẻ", "Scabies"),
    ("Mề đay", "Urticaria"),
    ("Viêm nang lông", "Folliculitis"),
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
