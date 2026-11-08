#!/usr/bin/env python3
"""Build 062: decode the VSUB.xyzw VFdest,VF0,VF0 BIOS initialization family."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 062 anchor mismatch {path}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t vu0_vsub_vf2_writes;","uint64_t vu0_vsub_vf2_writes;uint64_t vu0_vsub_family_writes;uint64_t vu0_vsub_family_by_dest[32];")
p=root/"source/emu_core.cpp"
change(p,"vu0_vsub_vf2_writes=0;","vu0_vsub_vf2_writes=0;vu0_vsub_family_writes=0;memset(vu0_vsub_family_by_dest,0,sizeof(vu0_vsub_family_by_dest));")
change(p,'''else if(opcode==0x4BE000ACu){
   // VSUB.xyzw VF2,VF0,VF0; exact BIOS initialization case.
   // VF0 is hardwired (0,0,0,1). No generic vector arithmetic or flags.
   vu0_vf[2][0]=0;vu0_vf[2][1]=0;vu0_vf[2][2]=0;vu0_vf[2][3]=0;
   ++vu0_vsub_vf2_writes;write=false;
  }
  else if(opcode==0x4BE0006Cu){
   // VSUB.xyzw VF1,VF0,VF0: exact BIOS instruction.
   // VF0 is hardwired (0,0,0,1); subtracting it from itself yields
   // positive zero in all four VF1 lanes. Generic VSUB and flags
   // are not implemented yet.
   vu0_vf[1][0]=0;vu0_vf[1][1]=0;vu0_vf[1][2]=0;vu0_vf[1][3]=0;
   ++vu0_vsub_vf0_writes;write=false;
  }''','''else if((opcode&0xFFFFF83Fu)==0x4BE0002Cu){
   // VSUB.xyzw VFdest,VF0,VF0; mask excludes only destination bits 10:6.
   // VF0 is hardwired (0,0,0,1). Equal operands produce +0 in each lane.
   // This narrow handler does not implement generic VSUB or status flags.
   unsigned dest=(opcode>>6)&31u;
   if(dest!=0u){
    for(unsigned lane=0;lane<4;++lane)vu0_vf[dest][lane]=0;
    ++vu0_vsub_family_writes;++vu0_vsub_family_by_dest[dest];
    if(dest==1u)++vu0_vsub_vf0_writes;
    if(dest==2u)++vu0_vsub_vf2_writes;
   }
   write=false;
  }''')
change(p,'fprintf(f,"VU0 VSUB.xyzw VF2,VF0,VF0 exact writes=', 'fprintf(f,"VU0 VSUB.xyzw VFdest,VF0,VF0 family writes=%llu VF3=%08X,%08X,%08X,%08X VF3_WRITES=%llu (generic VSUB/flags unsupported)\\n",(unsigned long long)vu0_vsub_family_writes,vu0_vf[3][0],vu0_vf[3][1],vu0_vf[3][2],vu0_vf[3][3],(unsigned long long)vu0_vsub_family_by_dest[3]);\n fprintf(f,"VU0 VSUB.xyzw VF2,VF0,VF0 exact writes=')
change(root/"source/emu_ui.inc","BUILD 061 - VU0 VSUB VF2","BUILD 062 - VU0 VSUB DECODE")
print("Build 062 decoded VU0 VSUB VFdest,VF0,VF0 family applied")
