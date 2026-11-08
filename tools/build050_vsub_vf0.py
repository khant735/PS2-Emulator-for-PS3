#!/usr/bin/env python3
"""Build 050: exact VSUB.xyzw VF1,VF0,VF0 BIOS initialization case."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 050 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t vu0_qmfc2_reads;","uint64_t vu0_qmfc2_reads;uint64_t vu0_vsub_vf0_writes;")
p=root/"source/emu_core.cpp"
change(p,"vu0_qmfc2_reads=0;","vu0_qmfc2_reads=0;vu0_vsub_vf0_writes=0;")
change(p,'''else if(opcode==0x4BE0006Cu){
   // VU macro opcode encountered during VU1 initialization.
   // Deliberately halt: no fabricated vector result or state changes.
   return halt(UNSUPPORTED,"VU macro 4BE0006C: rs=31 rt=0 rd=0 sa=1 fn=2C; semantics pending verification");
  }''','''else if(opcode==0x4BE0006Cu){
   // VSUB.xyzw VF1,VF0,VF0: exact BIOS instruction.
   // VF0 is hardwired (0,0,0,1); subtracting it from itself yields
   // positive zero in all four VF1 lanes. Generic VSUB and flags
   // are not implemented yet.
   vu0_vf[1][0]=0;vu0_vf[1][1]=0;vu0_vf[1][2]=0;vu0_vf[1][3]=0;
   ++vu0_vsub_vf0_writes;write=false;
  }''')
change(p,'fprintf(f,"VU0 QMFC2 128-bit VF reads=', 'fprintf(f,"VU0 VSUB.xyzw VF1,VF0,VF0 exact writes=%llu VF1=%08X,%08X,%08X,%08X (generic VSUB/flags unsupported)\\n",(unsigned long long)vu0_vsub_vf0_writes,vu0_vf[1][0],vu0_vf[1][1],vu0_vf[1][2],vu0_vf[1][3]);\n fprintf(f,"VU0 QMFC2 128-bit VF reads=')
change(root/"source/emu_ui.inc","BUILD 049 - VU MACRO DECODE","BUILD 050 - VU VSUB VF0")
print("Build 050 exact VSUB VF1,VF0,VF0 applied")
