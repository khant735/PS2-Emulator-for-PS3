#!/usr/bin/env python3
"""Build 061: exact BIOS VU0 VSUB.xyzw VF2,VF0,VF0 case."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 061 anchor mismatch {path}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t vu0_vsub_vf0_writes;","uint64_t vu0_vsub_vf0_writes;uint64_t vu0_vsub_vf2_writes;")
p=root/"source/emu_core.cpp"
change(p,"vu0_vsub_vf0_writes=0;","vu0_vsub_vf0_writes=0;vu0_vsub_vf2_writes=0;")
change(p,"else if(opcode==0x4BE0006Cu){",'''else if(opcode==0x4BE000ACu){
   // VSUB.xyzw VF2,VF0,VF0; exact BIOS initialization case.
   // VF0 is hardwired (0,0,0,1). No generic vector arithmetic or flags.
   vu0_vf[2][0]=0;vu0_vf[2][1]=0;vu0_vf[2][2]=0;vu0_vf[2][3]=0;
   ++vu0_vsub_vf2_writes;write=false;
  }
  else if(opcode==0x4BE0006Cu){''')
change(p,'fprintf(f,"VU0 VSUB.xyzw VF1,VF0,VF0 exact writes=', 'fprintf(f,"VU0 VSUB.xyzw VF2,VF0,VF0 exact writes=%llu VF2=%08X,%08X,%08X,%08X (flags unsupported)\\n",(unsigned long long)vu0_vsub_vf2_writes,vu0_vf[2][0],vu0_vf[2][1],vu0_vf[2][2],vu0_vf[2][3]);\n fprintf(f,"VU0 VSUB.xyzw VF1,VF0,VF0 exact writes=')
change(root/"source/emu_ui.inc","BUILD 060 - VU0 RAM","BUILD 061 - VU0 VSUB VF2")
print("Build 061 exact VU0 VF2 initialization applied")
