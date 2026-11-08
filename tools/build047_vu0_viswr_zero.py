#!/usr/bin/env python3
"""Build 047: exact VU0 VISWR VF0, VI0 initialization write.
Opcode 4B000BFF is VISWR.x VF0, (VI0), NOT VNOP.
Only this zero-register case is implemented; no generic VU execution.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 047 anchor mismatch {path}: {a[:110]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t vu0_control[32];","uint32_t vu0_data[1024];uint64_t vu0_viswr_zero_writes;uint32_t vu0_control[32];")
p=root/"source/emu_core.cpp"
change(p,"memset(vu0_control,0,sizeof(vu0_control));","memset(vu0_control,0,sizeof(vu0_control));memset(vu0_data,0,sizeof(vu0_data));vu0_viswr_zero_writes=0;")
change(p,'else if(rs==6){vu0_control[rd]=uint32_t(b);++vu0_ctc2_writes;write=false;}',
'''else if(rs==6){vu0_control[rd]=uint32_t(b);++vu0_ctc2_writes;write=false;}
  else if(rs==24 && rt==0 && rd==0 && fn==63 && ((opcode>>6)&31u)==15u){
   // COP2 SPECIAL2 index 63: VISWR.x VF0,(VI0).
   // VF0.x is the hardwired zero constant; VI0 is the hardwired zero address.
   // VU0 data memory is 4 KiB. Only the observed zero-register case is supported.
   vu0_data[0]=0;++vu0_viswr_zero_writes;write=false;
  }''')
change(p,'fprintf(f,"VU0 COP2 control storage','fprintf(f,"VU0 VISWR.x VF0,(VI0) exact opcode: WRITES=%llu DATA0=%08X (other VU ops unsupported)\\n",(unsigned long long)vu0_viswr_zero_writes,vu0_data[0]);\n fprintf(f,"VU0 COP2 control storage')
change(root/"source/emu_ui.inc","BUILD 046 - VU0 COP2 CONTROL","BUILD 047 - VU0 VISWR ZERO")
print("Build 047 exact VU0 VISWR zero-register case applied")
