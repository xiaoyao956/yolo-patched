#!/usr/bin/env python3
"""
Strategy: Full CArchive rebuild preserving original binary layout.
- Read original exe
- Extract PE header prefix (before archive start)
- Read all data entries from original (decompressed)
- Replace main.py and PYZ data
- Compress entries back (matching original comp flags)
- Rebuild TOC with exact entry_length, padding, and alignment
- Rebuild cookie with correct pyvers
- Combine prefix + data + TOC + cookie
"""
import sys, os, struct, marshal, zlib

BASE = r"e:/BaiduNetdiskDownload\YOLO_Annotation_Tool_Pro"
ORIG = os.path.join(BASE, "YOLO_Annotation_Tool_Pro.exe")
OUT = os.path.join(BASE, "YOLO_Annotation_Tool_Pro_Patched.exe")
NEW_PYZ = os.path.join(BASE, "_decompiled", "build", "PYZ.pyz")
PATCH_PYC = os.path.join(BASE, "_decompiled", "pyc311")

sys.path[:0] = ["C:/Users/xiaoyao/AppData/Local/Programs/Python/Python311/Lib/site-packages"]
from PyInstaller.archive.readers import CArchiveReader

# Read original structure
a = CArchiveReader(ORIG)
ARCHIVE_START = a._start_offset
print(f"Archive start: {ARCHIVE_START}")

with open(ORIG, 'rb') as f:
    orig = f.read()
prefix = orig[:ARCHIVE_START]

# New PYZ and main
with open(NEW_PYZ, 'rb') as f:
    new_pyz = f.read()
with open(os.path.join(PATCH_PYC, 'main.pyc'), 'rb') as f:
    f.read(16)
    new_main_data = f.read()

# Ordered entries (must match original order for TOC)
ORDER = ['struct', 'pyimod01_archive', 'pyimod02_importers', 'pyimod03_ctypes',
         'pyimod04_pywin32', 'pyiboot01_bootstrap', 'pyi_rth_openssl', 'pyi_rth_inspect',
         'pyi_rth_pkgutil', 'pyi_rth_setuptools', 'pyi_rth_pywintypes', 'pyi_rth_pythoncom',
         'pyi_rth__tkinter', 'pyi_rth_tensorflow', 'pyi_rth_pyqtgraph_multiprocess',
         'pyi_rth_mplconfig', 'pyi_rth_pyside6', 'pyi_rth_multiprocessing', 'main', 'PYZ.pyz']

# Read original entries, decompress
orig_entries = {}
for name, (off, ln, ul, comp, typ) in a.toc.items():
    raw = orig[ARCHIVE_START + off: ARCHIVE_START + off + ln]
    if comp:
        raw = zlib.decompress(raw)
    orig_entries[name] = (raw, comp, ul, typ)

# Build new archive data and TOC
NEW_DATA = bytearray()
TOC_BIN = bytearray()

# TOC entry header format: entry_length(4) + offset(4) + length(4) + ulen(4) + comp(1) + type(1) + name\0 + padding
ENTRY_HDR = struct.Struct('!IIIIBc')

for name in ORDER:
    raw_data, comp_flag, ulen, typ = orig_entries[name]

    if name == 'main':
        raw_data = new_main_data
        ulen = len(new_main_data)
        comp_flag = 1
        typ = 's'
    elif name == 'PYZ.pyz':
        raw_data = new_pyz
        ulen = len(new_pyz)
        comp_flag = 0
        typ = 'z'

    # Compress if needed
    if comp_flag:
        data_to_store = zlib.compress(raw_data)
    else:
        data_to_store = raw_data

    entry_offset = len(NEW_DATA)  # relative to archive start
    NEW_DATA.extend(data_to_store)

    # Build TOC entry
    # CArchive TOC entry: fixed header + name\0 + padding to 16 bytes
    name_b = name.encode('utf-8') + b'\x00'
    raw_entry_len = ENTRY_HDR.size + len(name_b)
    pad = (16 - (raw_entry_len % 16)) % 16
    entry_length = raw_entry_len + pad

    TOC_BIN.extend(ENTRY_HDR.pack(entry_length, entry_offset, len(data_to_store), ulen, comp_flag, typ.encode()))
    TOC_BIN.extend(name_b)
    TOC_BIN.extend(b'\x00' * pad)

TOC_LEN = len(TOC_BIN)
DATA_LEN = len(NEW_DATA)

# Build cookie
COOKIE_FMT = struct.Struct('!8sIIII64s')
COOKIE_LEN = COOKIE_FMT.size
TOC_OFF = DATA_LEN
# archive_length = data + TOC + cookie
ARCHIVE_LEN = DATA_LEN + TOC_LEN + COOKIE_LEN

cookie = COOKIE_FMT.pack(
    b'MEI\014\013\012\013\016',
    ARCHIVE_LEN,
    TOC_OFF,
    TOC_LEN,
    0x137,  # Python 3.11: 311 = 3*100+11
    b'python311.dll\x00'
)

# Build final file
final = bytearray()
final.extend(prefix)  # PE header
final.extend(NEW_DATA)  # all data blocks
final.extend(TOC_BIN)  # TOC
final.extend(cookie)  # cookie at end

with open(OUT, 'wb') as f:
    f.write(bytes(final))

print(f"Written: {OUT}")
print(f"Size: {len(final):,} bytes (orig: {len(orig):,})")

# Verify
v = CArchiveReader(OUT)
print(f"\n=== Verification ===")
print(f"Entries: {len(v.toc)}")

for name in ORDER:
    off, ln, ul, comp, typ = v.toc[name]
    if name in ('main', 'PYZ.pyz', 'struct', 'pyiboot01_bootstrap'):
        print(f"  {name:35s} off={off:5d} len={ln:8d} ulen={ul:8d} comp={comp} type={typ}")

# Check main
main_raw = v.extract('main')
mc = marshal.loads(main_raw)
print(f"\nmain.py: {mc.co_filename}")
print(f"  names: {list(mc.co_names)}")

# Check PYZ
pyz_raw = v.extract('PYZ.pyz')
print(f"PYZ: {len(pyz_raw)} bytes")

toc_off = struct.unpack('!i', pyz_raw[8:12])[0]
pyz_toc = marshal.loads(pyz_raw[toc_off:])
for item in pyz_toc:
    if isinstance(item, tuple) and item[0] == 'app_config.version':
        flag, pos, size = item[1]
        raw = pyz_raw[pos:pos+size]
        if flag == 0:
            raw = zlib.decompress(raw)
        vc = marshal.loads(raw)
        for c in vc.co_consts:
            if isinstance(c, str) and '9.9' in c:
                print(f"version: {c}")
        break

print(f"\nReady!")
