#!/usr/bin/env python3
"""Build 048: VU0 VF register storage and QMFC2 128-bit transfer."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 048 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t vu0_data[1024];","uint32_t vu0_vf[32][4];uint64_t vu0_qmfc2_reads;uint32_t vu0_data[1024];")
p=root/"source/emu_core.cpp"
change(p,"memset(vu0_data,0,sizeof(vu0_data));vu0_viswr_zero_writes=0;","memset(vu0_data,0,sizeof(vu0_data));vu0_viswr_zero_writes=0;memset(vu0_vf,0,sizeof(vu0_vf));vu0_vf[0][3]=0x3F800000u;vu0_qmfc2_reads=0;")
change(p,"if(rs==2){result=sx32(vu0_control[rd]);++vu0_cfc2_reads;}","""if(rs==1){
   // QMFC2 rt,VF[rd]: four raw 32-bit lanes, EE 128-bit GPR destination.
   // VF0 is the VU constant (0,0,0,1). No VU arithmetic is simulated.
   uint64_t lo=uint64_t(vu0_vf[rd][0])|(uint64_t(vu0_vf[rd][1])<<32);
   uint64_t hi=uint64_t(vu0_vf[rd][2])|(uint64_t(vu0_vf[rd][3])<<32);
   result=lo;
   if(rt)reg_hi[rt]=hi;
   ++vu0_qmfc2_reads;
  }
  else if(rs==2){result=sx32(vu0_control[rd]);++vu0_cfc2_reads;}""")
change(p,'fprintf(f,"VU0 VISWR.x VF0,(VI0) exact opcode:', 'fprintf(f,"VU0 QMFC2 128-bit VF reads=%llu VF1=%08X,%08X,%08X,%08X (no VU arithmetic)\\n",(unsigned long long)vu0_qmfc2_reads,vu0_vf[1][0],vu0_vf[1][1],vu0_vf[1][2],vu0_vf[1][3]);\n fprintf(f,"VU0 VISWR.x VF0,(VI0) exact opcode:')
change(root/"source/emu_ui.inc","BUILD 047 - VU0 VISWR ZERO","BUILD 048 - VU0 QMFC2")
print("Build 048 VU0 QMFC2 patch applied")
