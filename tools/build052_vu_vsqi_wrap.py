#!/usr/bin/env python3
"""Build 052: VU0 VSQI 4 KiB local data-memory address wrapping."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 052 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
p=root/"source/emu_core.cpp"
change(p,'''const uint32_t slot=vu0_control[1]&0xffffu;
   if(slot>=256u)return halt(UNSUPPORTED,"VSQI VI1 outside VU0 4 KiB data memory");''','''const uint32_t slot=vu0_control[1]&0xffu;
   // VU0 4 KiB data memory wraps at 256 qwords. VI1 itself remains 16-bit.''')
change(p,'VU0 VSQI.xyzw VF1,(VI1++) writes=%llu last_slot=%u VI1=%04X DATA[0]=%08X,%08X,%08X,%08X','VU0 VSQI.xyzw VF1,(VI1++) writes=%llu last_slot=%u VI1=%04X DATA[0]=%08X,%08X,%08X,%08X')
change(root/"source/emu_ui.inc","BUILD 051 - VU VSQI VF1","BUILD 052 - VU VSQI WRAP")
print("Build 052 VU0 VSQI wrapped address applied")
