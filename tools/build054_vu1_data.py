#!/usr/bin/env python3
"""Build 054: 16 KiB VU1 data-memory window, 128-bit EE SQ/SQ loads."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 054 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t vu0_data[1024];","unsigned char vu1_data[16384];uint64_t vu1_qword_writes,vu1_qword_reads;uint32_t vu1_last_offset;uint32_t vu0_data[1024];")
p=root/"source/emu_core.cpp"
change(p,"memset(vu0_data,0,sizeof(vu0_data));","memset(vu1_data,0,sizeof(vu1_data));vu1_qword_writes=vu1_qword_reads=0;vu1_last_offset=0;memset(vu0_data,0,sizeof(vu0_data));")
change(p,"  if(!p)return memoryHalt(aligned,16,store,false);",'''  // VU1 data memory is 16 KiB at physical 0x1100C000-0x1100FFFF.
  // Do not alias adjacent VU1 micro memory (0x11000000).
  uint32_t vu1_physical=0;
  bool vu1_access=false;
  if(!p && translate(aligned,16,store,vu1_physical) &&
     vu1_physical>=0x1100C000u && vu1_physical<=0x1100FFF0u){
   vu1_last_offset=vu1_physical-0x1100C000u;
   p=vu1_data+vu1_last_offset;
   vu1_access=true;
  }
  if(!p)return memoryHalt(aligned,16,store,false);''')
change(p,"  if(store){uint64_t lower=rt?reg[rt]:0,upper=rt?reg_hi[rt]:0;",'''  if(vu1_access){if(store)++vu1_qword_writes;else ++vu1_qword_reads;}
  if(store){uint64_t lower=rt?reg[rt]:0,upper=rt?reg_hi[rt]:0;''')
change(p,'fprintf(f,"VU0 VSQI.xyzw VF1,(VI1++) writes=', 'fprintf(f,"VU1 data 16KiB SQ_WRITES=%llu LQ_READS=%llu LAST_OFFSET=%04X DATA[0]=%02X,%02X,%02X,%02X\\n",(unsigned long long)vu1_qword_writes,(unsigned long long)vu1_qword_reads,vu1_last_offset,vu1_data[0],vu1_data[1],vu1_data[2],vu1_data[3]);\n fprintf(f,"VU0 VSQI.xyzw VF1,(VI1++) writes=')
change(root/"source/emu_ui.inc","BUILD 053 - VU QMTC2","BUILD 054 - VU1 DATA RAM")
print("Build 054 VU1 data-memory SQ/LQ mapping applied")
