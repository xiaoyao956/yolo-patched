#!/usr/bin/env python3
"""
Strategy: In-place binary patching.
Replace PYZ data at original offset (size differs - pad to match).
Replace main.py at original offset (if size differs, pad to match).
Update TOC entries that changed.
Update the cookie if TOC changed.
"""
import sys, os, struct, marshal, zlib

BASE = r"e:/BaiduNetdiskDownload\YOLO_Annotation_Tool_Pro"
ORIG = os.path.join(BASE, "YOLO_Annotation_Tool_Pro.exe")
OUT = os.path.join(BASE, "YOLO_Annotation_Tool_Pro_Patched.exe")
NEW_PYZ = os.path.join(BASE, "_decompiled", "build", "PYZ.pyz")
PATCH_PYC = os.path.join(BASE, "_decompiled", "pyc311")
PY3 = "C:/Users/xiaoyao/AppData/Local/Programs/Python/Python311/python.exe"

sys.path[:0] = [os.path.join(os.path.dirname(PY3), "Lib", "site-packages")]
from PyInstaller.archive.readers import CArchiveReader

# Copy original first
import shutil
shutil.copy2(ORIG, OUT)

a = CArchiveReader(OUT)
ARCHIVE_START = a._start_offset

with open(OUT, 'rb') as f:
    exe = bytearray(f.read())

# Get original PYZ size and position
pyz_off, pyz_len, pyz_ulen, pyz_comp, pyz_type = a.toc['PYZ.pyz']
main_off, main_len, main_ulen, main_comp, main_type = a.toc['main']
print(f"Original:")
print(f"  PYZ:  offset={pyz_off}, len={pyz_len}")
print(f"  main: offset={main_off}, len={main_len}, comp={main_comp}")

# Read new PYZ
with open(NEW_PYZ, 'rb') as f:
    new_pyz = f.read()
with open(os.path.join(PATCH_PYC, 'main.pyc'), 'rb') as f:
    f.read(16)
    new_main_code = f.read()
new_main_comp = zlib.compress(new_main_code)

# Read new PYZ size difference
pyz_size_diff = len(new_pyz) - pyz_len
main_size_diff = len(new_main_comp) - main_len
print(f"\nSize differences:")
print(f"  PYZ:  {len(new_pyz)} vs {pyz_len} (delta={pyz_size_diff})")
print(f"  main: {len(new_main_comp)} vs {main_len} (delta={main_size_diff})")

# ================================================================
# PYZ replacement at original offset - pad to original size
# ================================================================
abs_pyz_start = ARCHIVE_START + pyz_off
if len(new_pyz) <= pyz_len:
    # Pad to original size
    padded_pyz = bytearray(new_pyz)
    padded_pyz.extend(b'\x00' * (pyz_len - len(new_pyz)))
    exe[abs_pyz_start:abs_pyz_start + pyz_len] = padded_pyz
    print(f"\nOK: PYZ replaced in-place (padded to {pyz_len} bytes)")
else:
    print(f" PYZ too large ({len(new_pyz)} > {pyz_len}), cannot in-place patch")
    sys.exit(1)

# ================================================================
# main.py replacement - pad to original size
# ================================================================
abs_main_start = ARCHIVE_START + main_off
if len(new_main_comp) <= main_len:
    padded_main = bytearray(new_main_comp)
    padded_main.extend(b'\x00' * (main_len - len(new_main_comp)))
    exe[abs_main_start:abs_main_start + main_len] = padded_main
    print(f" main.py replaced in-place (padded to {main_len} bytes)")
else:
    print(f" main.py too large ({len(new_main_comp)} > {main_len})")
    sys.exit(1)

# ================================================================
# Update the CArchive TOC entry for main (PYZ entry unchanged since same size)
# The TOC is stored at the end of archive, before the cookie
# Need to find and update main's entry
# ================================================================

# Read the cookie
MEI_MAGIC = b'MEI\014\013\012\013\016'
cookie_start = exe.rfind(MEI_MAGIC)
assert cookie_start >= 0, "Cookie not found!"
COOKIE_FMT = '!8sIIII64s'
COOKIE_LEN = struct.calcsize(COOKIE_FMT)
m, archive_length, toc_offset, toc_length, pyvers, pylib_name = struct.unpack(COOKIE_FMT, exe[cookie_start:cookie_start+COOKIE_LEN])

print(f"\nCookie state:")
print(f"  archive_length: {archive_length}")
print(f"  toc_offset: {toc_offset}")
print(f"  toc_length: {toc_length}")

# Read the TOC
ENTRY_HDR_FMT = '!IIIIBc'
ENTRY_HDR_LEN = struct.calcsize(ENTRY_HDR_FMT)
toc_abs_start = ARCHIVE_START + toc_offset
toc_raw = bytes(exe[toc_abs_start:toc_abs_start + toc_length])

# Parse and rebuild TOC binary with corrected main entry
new_toc = bytearray()
pos = 0
entries_found = 0
while pos < len(toc_raw):
    # Parse header
    entry_length, entry_offset, data_length, ulen, comp_flag, typ = struct.unpack(ENTRY_HDR_FMT, toc_raw[pos:pos+ENTRY_HDR_LEN])
    # Read name
    name_start = pos + ENTRY_HDR_LEN
    name_end = toc_raw.find(b'\x00', name_start)
    name = toc_raw[name_start:name_end].decode('utf-8')

    # Check if this is the PYZ entry - update uncompressed length (since it's padded, compressed size same)
    if name == 'PYZ.pyz':
        # PYZ entry: data_length unchanged (same size), ulen = original PYZ size
        new_entry = struct.pack(ENTRY_HDR_FMT, entry_length, entry_offset, data_length, pyz_ulen, comp_flag, typ)
        new_toc.extend(new_entry)
        new_toc.extend(toc_raw[name_start:pos+entry_length])
        print(f"  PYZ TOC entry kept (ulen={pyz_ulen})")
    elif name == 'main':
        # main entry: data_length = padded length (same as original), ulen = new uncompressed
        new_entry = struct.pack(ENTRY_HDR_FMT, entry_length, entry_offset, main_len, len(new_main_code), 1, typ)
        new_toc.extend(new_entry)
        new_toc.extend(toc_raw[name_start:pos+entry_length])
        print(f"  main TOC entry updated: len={main_len}, ulen={len(new_main_code)}")
    else:
        # Keep original
        new_toc.extend(toc_raw[pos:pos+entry_length])

    pos += entry_length
    entries_found += 1

# Replace TOC in exe
if len(new_toc) != toc_length:
    print(f" TOC size changed: {len(new_toc)} vs {toc_length}")
    # Can't do in-place if TOC size changes - would need full rebuild
    # This shouldn't happen since we kept entry_length for each entry
    print(f"TOC entry count: {entries_found}")

    # If only specific entries changed, we can update in-place
    # Check if size really changed
    if abs(len(new_toc) - toc_length) > 4:
        print("TOC size mismatch - need different approach")
    else:
        exe[toc_abs_start:toc_abs_start + toc_length] = bytes(new_toc[:toc_length])
else:
    exe[toc_abs_start:toc_abs_start + toc_length] = bytes(new_toc)
print(f" TOC updated")

# Write output
with open(OUT, 'wb') as f:
    f.write(bytes(exe))

# Verify
v = CArchiveReader(OUT)
print(f"\n=== Final Verification ===")
print(f"Entries: {len(v.toc)}")

for name in ['main', 'PYZ.pyz']:
    off, ln, ul, comp, typ = v.toc[name]
    print(f"  {name}: off={off}, len={ln}, ulen={ul}, comp={comp}")

main_data = v.extract('main')
mc = marshal.loads(main_data)
print(f"\nmain.py: {mc.co_filename}")

pyz_data = v.extract('PYZ.pyz')
print(f"PYZ: {len(pyz_data)} bytes (original: {pyz_len})")

# Check version - parse without trimming
toc_off = struct.unpack('!i', pyz_data[8:12])[0]
if toc_off < len(pyz_data):
    pyz_toc = marshal.loads(pyz_data[toc_off:])
    for item in pyz_toc:
        if isinstance(item, tuple) and item[0] == 'app_config.version':
            flag, pos, size = item[1]
            raw = pyz_data[pos:pos+size]
            if flag == 0:
                raw = zlib.decompress(raw)
            vc = marshal.loads(raw)
            for c in vc.co_consts:
                if isinstance(c, str) and ('9.9' in str(c)):
                    print(f"version: {c}")
            break
else:
    print(f"(TOC at offset {toc_off} is beyond padded PYZ length {len(pyz_data)} - expected, padding truncated)")

print(f"\n Output: {OUT}")
print(f"   Size: {os.path.getsize(OUT):,} bytes")
