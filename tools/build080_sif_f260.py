#!/usr/bin/env python3
"""Build 080: exact EE SIF 0x1000F260 experimental register latch."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build 080 anchor mismatch: {path} {old[:80]!r} count={s.count(old)}")
 path.write_text(s.replace(old,new,1))
h=root/"include/emu_core.h"
change(h,"uint32_t ee_sif_ctrl;","uint32_t ee_sif_f260;uint64_t ee_sif_f260_reads,ee_sif_f260_writes;uint32_t ee_sif_f260_last_pc,ee_sif_f260_last_value;uint32_t ee_sif_ctrl;")
p=root/"source/emu_core.cpp"
change(p,"ee_sif_ctrl=0;","ee_sif_f260=0;ee_sif_f260_reads=ee_sif_f260_writes=0;ee_sif_f260_last_pc=ee_sif_f260_last_value=0;ee_sif_ctrl=0;")
s=p.read_text()
for method,body in [
 ("mmioRead",''' if(size==4 && (a&0x1FFFFFFFu)==0x1000F260u){
  // Experimental SIF register storage; no IOP or interrupt side effects.
  v=ee_sif_f260;++ee_sif_f260_reads;ee_sif_f260_last_pc=pc;return true;
 }
'''),
 ("mmioWrite",''' if(size==4 && (a&0x1FFFFFFFu)==0x1000F260u){
  // Exact-address capture only; register semantics still unverified.
  ee_sif_f260=uint32_t(v);++ee_sif_f260_writes;
  ee_sif_f260_last_pc=pc;ee_sif_f260_last_value=uint32_t(v);return true;
 }
''')]:
 pattern=r"(bool\s+Core::"+method+r"\s*\([^)]*\)\s*\{)"
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build 080 cannot locate {method}: {len(matches)}")
 m=matches[0];s=s[:m.end()]+"\n"+body+s[m.end():]
p.write_text(s)
change(p,'fprintf(f,"EE SDL/SDR little-endian stores:', 'fprintf(f,"EE SIF 1000F260 experimental latch (no IOP effects): VALUE=%08X READS=%llu WRITES=%llu LAST_PC=%08X LAST_WRITE=%08X\\n",ee_sif_f260,(unsigned long long)ee_sif_f260_reads,(unsigned long long)ee_sif_f260_writes,ee_sif_f260_last_pc,ee_sif_f260_last_value);\n fprintf(f,"EE SDL/SDR little-endian stores:')
change(root/"source/emu_ui.inc","BUILD 079 - EE SIF ALIAS","BUILD 080 - EE SIF F260")
print("Build 080 exact SIF F260 diagnostic latch applied")
