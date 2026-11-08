#!/usr/bin/env python3
"""Build 056: VIF1 MMIO register subset; no VIF command engine or DMA."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 056 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"unsigned char vu1_micro[16384];","uint32_t vif1_regs[15];uint64_t vif1_writes,vif1_reads,vif1_fbrst_writes;uint32_t vif1_last_offset,vif1_last_value;unsigned char vu1_micro[16384];")
p=root/"source/emu_core.cpp"
change(p,"memset(vu1_micro,0,sizeof(vu1_micro));","memset(vif1_regs,0,sizeof(vif1_regs));vif1_writes=vif1_reads=vif1_fbrst_writes=0;vif1_last_offset=vif1_last_value=0;memset(vu1_micro,0,sizeof(vu1_micro));")
s=p.read_text()
# Match the actual MMIO function definitions and inject only inside those bodies.
for method,body in [
 ("mmioRead",''' if(size==4 && p>=0x10003C00u && p<=0x10003CE0u && ((p-0x10003C00u)&15u)==0){
  unsigned idx=(p-0x10003C00u)/16u;
  // VIF1 status and control registers: storage-only, no synthetic completion.
  v=vif1_regs[idx];++vif1_reads;vif1_last_offset=idx*16u;return true;
 }
'''),
 ("mmioWrite",''' if(size==4 && p>=0x10003C00u && p<=0x10003CE0u && ((p-0x10003C00u)&15u)==0){
  unsigned idx=(p-0x10003C00u)/16u;
  vif1_regs[idx]=uint32_t(v);++vif1_writes;
  vif1_last_offset=idx*16u;vif1_last_value=uint32_t(v);
  if(idx==1)++vif1_fbrst_writes; // FBRST command observed; no fake reset or FIFO processing.
  return true;
 }
''')]:
 pattern=r"(bool\s+Core::"+method+r"\s*\([^)]*\)\s*\{)"
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build 056 cannot locate {method}: {len(matches)}")
 m=matches[0];s=s[:m.end()]+"\n"+body+s[m.end():]
p.write_text(s)
change(p,'fprintf(f,"VU1 micro 16KiB SD_WRITES=', 'fprintf(f,"VIF1 register subset (no FIFO/DMA/IRQ): WRITES=%llu READS=%llu FBRST_WRITES=%llu LAST_OFFSET=%02X LAST_VALUE=%08X STAT=%08X FBRST=%08X\\n",(unsigned long long)vif1_writes,(unsigned long long)vif1_reads,(unsigned long long)vif1_fbrst_writes,vif1_last_offset,vif1_last_value,vif1_regs[0],vif1_regs[1]);\n fprintf(f,"VU1 micro 16KiB SD_WRITES=')
change(root/"source/emu_ui.inc","BUILD 055 - VU1 MICRO RAM","BUILD 056 - VIF1 REGISTERS")
print("Build 056 VIF1 register subset applied")
