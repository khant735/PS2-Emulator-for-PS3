#!/usr/bin/env python3
"""Build 046: VU0 COP2 control-register read/write diagnostic support.
No VU microexecution or DMA is simulated.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 046 anchor mismatch: {path} {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t dmac_channel_regs[10][7]","uint32_t vu0_control[32];uint64_t vu0_cfc2_reads,vu0_ctc2_writes;uint32_t dmac_channel_regs[10][7]")
p=root/"source/emu_core.cpp"
change(p,"dmac_global_writes=dmac_global_reads=0;","dmac_global_writes=dmac_global_reads=0;memset(vu0_control,0,sizeof(vu0_control));vu0_cfc2_reads=vu0_ctc2_writes=0;")
change(p,'}else return halt(UNSUPPORTED,"Primary instruction not implemented");',
''' }else if(op==18){
  // COP2 transfer instructions. This models only control-register storage.
  // rs=2: CFC2, rs=6: CTC2. No VU microprogram execution.
  if(rs==2){result=sx32(vu0_control[rd]);++vu0_cfc2_reads;}
  else if(rs==6){vu0_control[rd]=uint32_t(b);++vu0_ctc2_writes;write=false;}
  else return halt(UNSUPPORTED,"COP2 operation not implemented");
 }else return halt(UNSUPPORTED,"Primary instruction not implemented");''')
change(p,'fprintf(f,"EE DMAC register storage only','fprintf(f,"VU0 COP2 control storage (no VU execution): CFC2_READS=%llu CTC2_WRITES=%llu REG28=%08X\\n",(unsigned long long)vu0_cfc2_reads,(unsigned long long)vu0_ctc2_writes,vu0_control[28]);\n fprintf(f,"EE DMAC register storage only')
change(root/"source/emu_ui.inc","BUILD 045 - EE DMAC REGISTERS","BUILD 046 - VU0 COP2 CONTROL")
print("Build 046 VU0 COP2 control patch applied")
