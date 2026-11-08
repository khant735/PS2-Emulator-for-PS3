#!/usr/bin/env python3
"""Build 058: exact-address diagnostic storage for EE MMIO 0x1000F510.
The register semantics are not established; no DMA/TLB side effects are fabricated.
"""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 058 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t vif1_regs[15];","uint32_t f510_value,f510_last_write;uint64_t f510_reads,f510_writes;uint32_t vif1_regs[15];")
p=root/"source/emu_core.cpp"
change(p,"memset(vif1_regs,0,sizeof(vif1_regs));","f510_value=f510_last_write=0;f510_reads=f510_writes=0;memset(vif1_regs,0,sizeof(vif1_regs));")
s=p.read_text()
for method,body in [
 ("mmioRead",''' if(size==4 && a==0x1000F510u){v=f510_value;++f510_reads;return true;}
'''),
 ("mmioWrite",''' if(size==4 && a==0x1000F510u){f510_value=uint32_t(v);f510_last_write=uint32_t(v);++f510_writes;return true;}
''')]:
 pattern=r"(bool\\s+Core::"+method+r"\\s*\\([^)]*\\)\\s*\\{)"
 # Same function-header injection approach used in Build 056.
 pattern=r"(bool\s+Core::"+method+r"\s*\([^)]*\)\s*\{)"
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build 058 cannot locate {method}: {len(matches)}")
 m=matches[0];s=s[:m.end()]+"\n"+body+s[m.end():]
p.write_text(s)
change(p,'fprintf(f,"VIF1 FIFO ingress (capture only;', 'fprintf(f,"EE F510 exact-address diagnostic (semantics unknown; no DMA/TLB effects): VALUE=%08X LAST_WRITE=%08X READS=%llu WRITES=%llu\\n",f510_value,f510_last_write,(unsigned long long)f510_reads,(unsigned long long)f510_writes);\n fprintf(f,"VIF1 FIFO ingress (capture only;')
change(root/"source/emu_ui.inc","BUILD 057 - VIF1 FIFO INGRESS","BUILD 058 - EE F510 PROBE")
print("Build 058 F510 diagnostic MMIO storage applied")
