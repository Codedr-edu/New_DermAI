import struct

def parse_po(lines):
    messages = {}
    current_msgid = []
    current_msgstr = []
    state = 'SEARCH' # SEARCH, MSGID, MSGSTR

    def clean(s):
        if s.startswith('"') and s.endswith('"'):
            # This is a basic unescape for standard PO strings
            return s[1:-1].replace('\\n', '\n').replace('\\"', '"')
        return s

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if line.startswith('msgid "'):
            if state == 'MSGSTR':
                 id_s = "".join(current_msgid)
                 str_s = "".join(current_msgstr)
                 messages[id_s] = str_s
                 current_msgid = []
                 current_msgstr = []
            
            state = 'MSGID'
            current_msgid.append(clean(line[6:].strip()))
        
        elif line.startswith('msgstr "'):
            state = 'MSGSTR'
            current_msgstr.append(clean(line[7:].strip()))
            
        elif line.startswith('"'):
            s = clean(line)
            if state == 'MSGID':
                current_msgid.append(s)
            elif state == 'MSGSTR':
                current_msgstr.append(s)

    if state == 'MSGSTR':
         id_s = "".join(current_msgid)
         str_s = "".join(current_msgstr)
         messages[id_s] = str_s
    
    return messages

def compile_file(po_path, mo_path):
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    messages = parse_po(lines)
    
    # Sort keys
    keys = sorted(messages.keys())
    
    # Prepare tables
    offsets = []
    ids = []
    strs = []
    
    data = bytearray()
    
    # Magic
    magic = 0x950412de
    version = 0
    num_strings = len(keys)
    
    # Tables start after header (7 * 4 bytes = 28 bytes)
    id_table_offset = 28
    str_table_offset = id_table_offset + 8 * num_strings
    
    # Content starts after tables
    content_offset = str_table_offset + 8 * num_strings
    
    # We capture offsets relative to file start
    
    # Build content buffer first to know offsets
    content_buffer = bytearray()
    
    # 1. Original strings
    key_offsets = []
    for k in keys:
        # Encode
        b_key = k.encode('utf-8') + b'\0'
        key_offsets.append((len(b_key) - 1, content_offset + len(content_buffer)))
        content_buffer.extend(b_key)
        
    # 2. Translated strings
    val_offsets = []
    for k in keys:
        v = messages[k]
        b_val = v.encode('utf-8') + b'\0'
        val_offsets.append((len(b_val) - 1, content_offset + len(content_buffer)))
        content_buffer.extend(b_val)
        
    # Write Header
    output = bytearray()
    output.extend(struct.pack('<I', magic))
    output.extend(struct.pack('<I', version))
    output.extend(struct.pack('<I', num_strings))
    output.extend(struct.pack('<I', id_table_offset))
    output.extend(struct.pack('<I', str_table_offset))
    output.extend(struct.pack('<I', 0)) # hash size
    output.extend(struct.pack('<I', 0)) # hash offset
    
    # Write ID Table
    for length, offset in key_offsets:
        output.extend(struct.pack('<II', length, offset))
        
    # Write Str Table
    for length, offset in val_offsets:
        output.extend(struct.pack('<II', length, offset))
        
    # Write Content
    output.extend(content_buffer)
    
    with open(mo_path, 'wb') as f:
        f.write(output)
    print(f"Success: Compiled {po_path} -> {mo_path}")

if __name__ == "__main__":
    compile_file(r'c:\Users\anhhu\New_DermAI\locale\en\LC_MESSAGES\django.po', r'c:\Users\anhhu\New_DermAI\locale\en\LC_MESSAGES\django.mo')
