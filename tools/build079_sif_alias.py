#!/usr/bin/env python3
"""Build 079: correct undefined variable in Build 078 SIF MMIO dispatch."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
p=root/"source/emu_core.cpp"
s=p.read_text()
old="if(size==4 && p==0x1000F240u)"
assert s.count(old)==2,("expected both Build 078 SIF handlers",s.count(old))
# Normalize kseg0/kseg1 aliases locally, without changing other MMIO handlers.
p.write_text(s.replace(old,"if(size==4 && (a&0x1FFFFFFFu)==0x1000F240u)"))
u=root/"source/emu_ui.inc"
t=u.read_text()
assert t.count("BUILD 078 - EE SIF PHYS")==1
u.write_text(t.replace("BUILD 078 - EE SIF PHYS","BUILD 079 - EE SIF ALIAS"))
print("Build 079: SIF read/write compare masked kseg physical address")
