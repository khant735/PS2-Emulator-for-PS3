#!/usr/bin/env python3
"""Build 072: classify exact EE BIOS 0x1F803800 halfword probe; no fabricated MMIO response."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
p=root/"source/emu_core.cpp"
s=p.read_text()
anchor='fprintf(f,"EE CACHE op0C'
assert s.count(anchor)==1,("Build 072 trace anchor mismatch",s.count(anchor))
s=s.replace(anchor,'''fprintf(f,"EE BIOS 1F803800 probe: PC=%08X OPCODE=%08X PHYS=1F803800 SIZE=2 READ=1 CLASSIFICATION=%s\\n",pc,opcode,(pc==0x8000EF60u && opcode==0x944A0000u)?"observed unsupported MMIO (no synthesized value)":"not at known probe");
 '''+anchor,1)
p.write_text(s)
p=root/"source/emu_ui.inc";s=p.read_text();anchor="BUILD 071 - EE CACHE OP0C";assert s.count(anchor)==1;s=s.replace(anchor,"BUILD 072 - MMIO 3800 DIAG",1);p.write_text(s)
print("Build 072 exact-address diagnostic; unknown MMIO still faults")
