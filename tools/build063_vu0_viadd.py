#!/usr/bin/env python3
"""Build 063: implement COP2 VIADD (integer VU0 registers, 16-bit)."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 063 anchor mismatch {path}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t vu0_vsub_family_writes;","uint64_t vu0_viadd_count;uint32_t vu0_viadd_last_opcode;uint64_t vu0_vsub_family_writes;")
p=root/"source/emu_core.cpp"
change(p,"vu0_vsub_family_writes=0;","vu0_viadd_count=0;vu0_viadd_last_opcode=0;vu0_vsub_family_writes=0;")
change(p,"else if((opcode&0xFFFFF83Fu)==0x4BE0002Cu){",'''else if((opcode&0xFFE0003Fu)==0x4A000030u){
   // VIADD id,is,it: 16-bit integer addition, VI0 is hardwired zero.
   // COP2 macro Special1 function 0x30; no floating point Q involved.
   const unsigned id=(opcode>>6)&31u;
   const unsigned is=(opcode>>11)&31u;
   const unsigned it=(opcode>>16)&31u;
   const uint32_t lhs=is?vu0_control[is]&0xffffu:0u;
   const uint32_t rhs=it?vu0_control[it]&0xffffu:0u;
   if(id)vu0_control[id]=(vu0_control[id]&0xffff0000u)|((lhs+rhs)&0xffffu);
   ++vu0_viadd_count;vu0_viadd_last_opcode=opcode;write=false;
  }
  else if((opcode&0xFFFFF83Fu)==0x4BE0002Cu){''')
change(p,'fprintf(f,"VU0 VSUB.xyzw VFdest,VF0,VF0 family writes=', 'fprintf(f,"VU0 VIADD 16-bit integer ops=%llu LAST_OPCODE=%08X VI1=%04X (VI0 fixed zero)\\n",(unsigned long long)vu0_viadd_count,vu0_viadd_last_opcode,vu0_control[1]&0xffffu);\n fprintf(f,"VU0 VSUB.xyzw VFdest,VF0,VF0 family writes=')
change(root/"source/emu_ui.inc","BUILD 062 - VU0 VSUB DECODE","BUILD 063 - VU0 VIADD")
print("Build 063 VIADD integer VU0 operation applied")
