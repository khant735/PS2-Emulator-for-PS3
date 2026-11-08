#!/usr/bin/env python3
"""Build 066: IPU MMIO diagnostic register subset, no decoder or DMA."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 066 anchor mismatch {path}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t vif0_regs[15];","uint32_t ipu_regs[4];uint64_t ipu_writes,ipu_reads,ipu_ctrl_reset_requests;uint32_t ipu_last_offset,ipu_last_value;uint32_t vif0_regs[15];")
p=root/"source/emu_core.cpp"
change(p,"memset(vif0_regs,0,sizeof(vif0_regs));","memset(ipu_regs,0,sizeof(ipu_regs));ipu_writes=ipu_reads=ipu_ctrl_reset_requests=0;ipu_last_offset=ipu_last_value=0;memset(vif0_regs,0,sizeof(vif0_regs));")
s=p.read_text()
for method,body in [
 ("mmioRead",''' if(size==4 && a>=0x10002000u && a<=0x10002030u && ((a-0x10002000u)&15u)==0){
  unsigned idx=(a-0x10002000u)/16u;
  v=ipu_regs[idx];++ipu_reads;ipu_last_offset=idx*16u;return true;
 }
'''),
 ("mmioWrite",''' if(size==4 && a>=0x10002000u && a<=0x10002030u && ((a-0x10002000u)&15u)==0){
  unsigned idx=(a-0x10002000u)/16u;
  ipu_regs[idx]=uint32_t(v);++ipu_writes;
  ipu_last_offset=idx*16u;ipu_last_value=uint32_t(v);
  if(idx==1 && (uint32_t(v)&0x40000000u))++ipu_ctrl_reset_requests;
  // Register capture only: reset side effects, decoder, FIFO and DMA absent.
  return true;
 }
''')]:
 pattern=r"(bool\s+Core::"+method+r"\s*\([^)]*\)\s*\{)"
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build 066 cannot locate {method}: {len(matches)}")
 m=matches[0];s=s[:m.end()]+"\n"+body+s[m.end():]
p.write_text(s)
change(p,'fprintf(f,"VIF0 FIFO ingress (capture only;', 'fprintf(f,"IPU register capture (no decode/reset side effects/DMA): WRITES=%llu READS=%llu CTRL_RESET_REQUESTS=%llu LAST_OFFSET=%02X LAST_VALUE=%08X CMD=%08X CTRL=%08X BP=%08X TOP=%08X\\n",(unsigned long long)ipu_writes,(unsigned long long)ipu_reads,(unsigned long long)ipu_ctrl_reset_requests,ipu_last_offset,ipu_last_value,ipu_regs[0],ipu_regs[1],ipu_regs[2],ipu_regs[3]);\n fprintf(f,"VIF0 FIFO ingress (capture only;')
change(root/"source/emu_ui.inc","BUILD 065 - VIF0 FIFO INGRESS","BUILD 066 - IPU REGISTERS")
print("Build 066 IPU register capture applied")
