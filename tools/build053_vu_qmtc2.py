#!/usr/bin/env python3
"""Build 053: exact 128-bit QMTC2 $v1,VF1 in JR delay slot."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 053 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t vu0_qmfc2_reads;","uint64_t vu0_qmfc2_reads;uint64_t vu0_qmtc2_writes;")
p=root/"source/emu_core.cpp"
change(p,"vu0_qmfc2_reads=0;","vu0_qmfc2_reads=0;vu0_qmtc2_writes=0;")
change(p,'''else if(rs==2){result=sx32(vu0_control[rd]);++vu0_cfc2_reads;}''','''else if(opcode==0x48A30800u){
   // QMTC2 $v1,VF1: transfer all 128 raw bits, including the high GPR half.
   const uint64_t lo=b,hi=reg_hi[rt];
   vu0_vf[rd][0]=uint32_t(lo);
   vu0_vf[rd][1]=uint32_t(lo>>32);
   vu0_vf[rd][2]=uint32_t(hi);
   vu0_vf[rd][3]=uint32_t(hi>>32);
   ++vu0_qmtc2_writes;write=false;
  }
  else if(rs==2){result=sx32(vu0_control[rd]);++vu0_cfc2_reads;}''')
change(p,'fprintf(f,"VU0 QMFC2 128-bit VF reads=', 'fprintf(f,"VU0 QMTC2 128-bit VF writes=%llu VF1=%08X,%08X,%08X,%08X\\n",(unsigned long long)vu0_qmtc2_writes,vu0_vf[1][0],vu0_vf[1][1],vu0_vf[1][2],vu0_vf[1][3]);\n fprintf(f,"VU0 QMFC2 128-bit VF reads=')
change(root/"source/emu_ui.inc","BUILD 052 - VU VSQI WRAP","BUILD 053 - VU QMTC2")
print("Build 053 exact QMTC2 128-bit transfer applied")
