#!/usr/bin/env python3
"""Build 064: VIF0 register subset at 0x10003800..0x100038E0."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 064 anchor mismatch {path}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t vif1_regs[15];","uint32_t vif0_regs[15];uint64_t vif0_writes,vif0_reads,vif0_fbrst_writes;uint32_t vif0_last_offset,vif0_last_value;uint32_t vif1_regs[15];")
p=root/"source/emu_core.cpp"
change(p,"memset(vif1_regs,0,sizeof(vif1_regs));","memset(vif0_regs,0,sizeof(vif0_regs));vif0_writes=vif0_reads=vif0_fbrst_writes=0;vif0_last_offset=vif0_last_value=0;memset(vif1_regs,0,sizeof(vif1_regs));")
s=p.read_text()
for method,body in [
 ("mmioRead",''' if(size==4 && a>=0x10003800u && a<=0x100038E0u && ((a-0x10003800u)&15u)==0){
  unsigned idx=(a-0x10003800u)/16u;
  v=vif0_regs[idx];++vif0_reads;vif0_last_offset=idx*16u;return true;
 }
'''),
 ("mmioWrite",''' if(size==4 && a>=0x10003800u && a<=0x100038E0u && ((a-0x10003800u)&15u)==0){
  unsigned idx=(a-0x10003800u)/16u;
  vif0_regs[idx]=uint32_t(v);++vif0_writes;
  vif0_last_offset=idx*16u;vif0_last_value=uint32_t(v);
  if(idx==1)++vif0_fbrst_writes; // Capture FBRST only; no invented side effects.
  return true;
 }
''')]:
 pattern=r"(bool\\s+Core::"+method+r"\\s*\\([^)]*\\)\\s*\\{)"
 # use same tested expression as Build 056
 pattern=r"(bool\s+Core::"+method+r"\s*\([^)]*\)\s*\{)"
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build 064 cannot locate {method}: {len(matches)}")
 m=matches[0];s=s[:m.end()]+"\n"+body+s[m.end():]
p.write_text(s)
change(p,'fprintf(f,"VIF1 register subset', 'fprintf(f,"VIF0 register subset (storage only; no FIFO/DMA/IRQ): WRITES=%llu READS=%llu FBRST_WRITES=%llu LAST_OFFSET=%02X LAST_VALUE=%08X STAT=%08X FBRST=%08X\\n",(unsigned long long)vif0_writes,(unsigned long long)vif0_reads,(unsigned long long)vif0_fbrst_writes,vif0_last_offset,vif0_last_value,vif0_regs[0],vif0_regs[1]);\n fprintf(f,"VIF1 register subset')
change(root/"source/emu_ui.inc","BUILD 063 - VU0 VIADD","BUILD 064 - VIF0 REGISTERS")
print("Build 064 VIF0 register subset applied")
