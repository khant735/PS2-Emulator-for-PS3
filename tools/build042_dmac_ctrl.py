#!/usr/bin/env python3
"""Build 042: EE DMAC D_CTRL register storage, without transfer emulation."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h";s=h.read_text()
anchor="uint32_t gif_mode,gif_pause;"
assert s.count(anchor)==1
s=s.replace(anchor,"uint32_t dmac_ctrl;uint64_t dmac_ctrl_writes,dmac_ctrl_reads;"+anchor)
h.write_text(s)
p=root/"source/emu_core.cpp";s=p.read_text()
anchor="gif_mode=gif_pause=0;"
assert s.count(anchor)==1
s=s.replace(anchor,"dmac_ctrl=0;dmac_ctrl_writes=dmac_ctrl_reads=0;"+anchor)
# Discover the exact method signature, rather than assuming an argument name.
for method,body in (
 ("mmioWrite","if(p==0x10000010u && size==4){dmac_ctrl=uint32_t(value);++dmac_ctrl_writes;return true;}"),
 ("mmioRead","if(p==0x10000010u && size==4){value=dmac_ctrl;++dmac_ctrl_reads;return true;}")
):
 matches=list(re.finditer(r'bool\\s+Core::'+method+r'\\s*\\(([^)]*)\\)\\s*\\{',s))
 if len(matches)!=1:raise SystemExit("Cannot locate unique "+method+" signature")
 m=matches[0];params=m.group(1)
 # The source's existing MMIO handler uses p for physical address, v for value.
 # Bind from parameter declarations so an unsupported signature fails safely.
 fields=[x.strip() for x in params.split(',')]
 if len(fields)<3:raise SystemExit("Unexpected "+method+" params: "+params)
 def name(field):return re.search(r'([A-Za-z_]\\w*)\\s*$',field).group(1)
 names=[name(x) for x in fields]
 addr=names[0]
 width=next((n for n in names if n in ("size","bytes","width")),None)
 if not width:raise SystemExit("Unknown MMIO access-width argument: "+params)
 if method=="mmioWrite":
  val=names[-1]
  inserted=f"if({addr}==0x10000010u && {width}==4){{dmac_ctrl=uint32_t({val});++dmac_ctrl_writes;return true;}}"
 else:
  val=names[-1]
  inserted=f"if({addr}==0x10000010u && {width}==4){{{val}=dmac_ctrl;++dmac_ctrl_reads;return true;}}"
 s=s[:m.end()]+"\n  // EE DMAC D_CTRL: storage only, no DMA engine/IRQ side effects.\n  "+inserted+s[m.end():]
anchor='fprintf(f,"GIF control subset'
idx=s.find(anchor)
if idx<0:raise SystemExit("Cannot locate diagnostics")
s=s[:idx]+'''fprintf(f,"EE DMAC D_CTRL storage only (no DMA/IRQ): CTRL=%08X WRITES=%llu READS=%llu\\n",dmac_ctrl,(unsigned long long)dmac_ctrl_writes,(unsigned long long)dmac_ctrl_reads);
 '''+s[idx:]
p.write_text(s)
ui=root/"source/emu_ui.inc";s=ui.read_text();a="BUILD 041 - GIF FIFO INGRESS";assert s.count(a)==1;ui.write_text(s.replace(a,"BUILD 042 - EE DMAC CONTROL"))
print("Build 042 DMAC D_CTRL storage and readback installed")
