#!/usr/bin/env python3
"""Build 051: VSQI.xyzw VF1,(VI1++) with 16-byte VU0 memory and VI postincrement."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 051 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t vu0_vsub_vf0_writes;","uint64_t vu0_vsub_vf0_writes;uint64_t vu0_vsqi_writes;uint32_t vu0_vsqi_last_slot;")
p=root/"source/emu_core.cpp"
change(p,"vu0_vsub_vf0_writes=0;","vu0_vsub_vf0_writes=0;vu0_vsqi_writes=0;vu0_vsqi_last_slot=0;")
change(p,'''else return halt(UNSUPPORTED,"COP2 operation not implemented");''','''else if(opcode==0x4BE10B7Du){
   // VSQI.xyzw VF1,(VI1++), COP2 SPECIAL2 slot 0x35.
   // VI addressing is in 16-byte qwords; VI1 is 16-bit.
   const uint32_t slot=vu0_control[1]&0xffffu;
   if(slot>=256u)return halt(UNSUPPORTED,"VSQI VI1 outside VU0 4 KiB data memory");
   for(unsigned lane=0;lane<4;++lane)vu0_data[slot*4u+lane]=vu0_vf[1][lane];
   vu0_control[1]=(vu0_control[1]&0xffff0000u)|((slot+1u)&0xffffu);
   vu0_vsqi_last_slot=slot;++vu0_vsqi_writes;write=false;
  }
  else return halt(UNSUPPORTED,"COP2 operation not implemented");''')
change(p,'fprintf(f,"VU0 VSUB.xyzw VF1,VF0,VF0 exact writes=', 'fprintf(f,"VU0 VSQI.xyzw VF1,(VI1++) writes=%llu last_slot=%u VI1=%04X DATA[0]=%08X,%08X,%08X,%08X\\n",(unsigned long long)vu0_vsqi_writes,vu0_vsqi_last_slot,vu0_control[1]&0xffffu,vu0_data[0],vu0_data[1],vu0_data[2],vu0_data[3]);\n fprintf(f,"VU0 VSUB.xyzw VF1,VF0,VF0 exact writes=')
change(root/"source/emu_ui.inc","BUILD 050 - VU VSUB VF0","BUILD 051 - VU VSQI VF1")
print("Build 051 exact VSQI applied")
