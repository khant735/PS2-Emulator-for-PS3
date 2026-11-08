#!/usr/bin/env python3
"""Build 078: fix SIF CTRL dispatch to compare translated physical address."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
p=root/"source/emu_core.cpp"
s=p.read_text()
old="if(size==4 && a==0x1000F240u)"
assert s.count(old)==2,("expected exact read and write SIF handlers",s.count(old))
p.write_text(s.replace(old,"if(size==4 && p==0x1000F240u)"))
u=root/"source/emu_ui.inc"
t=u.read_text()
assert t.count("BUILD 077 - EE SIF CTRL")==1
u.write_text(t.replace("BUILD 077 - EE SIF CTRL","BUILD 078 - EE SIF PHYS"))
print("Build 078: SIF MMIO handlers use translated physical address")
