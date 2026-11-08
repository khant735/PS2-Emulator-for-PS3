#!/usr/bin/env python3
"""Build 060: exact VU0 micro/data backing for EE 128-bit accesses."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 060 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"unsigned char vu1_micro[16384];","unsigned char vu0_micro[4096];uint64_t vu0_micro_qwrites,vu0_micro_qreads,vu0_data_qwrites,vu0_data_qreads;uint32_t vu0_last_qoffset;unsigned char vu1_micro[16384];")
p=root/"source/emu_core.cpp"
change(p,"memset(vu1_micro,0,sizeof(vu1_micro));","memset(vu0_micro,0,sizeof(vu0_micro));vu0_micro_qwrites=vu0_micro_qreads=vu0_data_qwrites=vu0_data_qreads=0;vu0_last_qoffset=0;memset(vu1_micro,0,sizeof(vu1_micro));")
change(p,"  if(!p)return memoryHalt(aligned,16,store,false);",'''  // Exact 4 KiB VU0 windows; data shares the existing VU0 backing store.
  if(!p){
   uint32_t vu0_physical=0;
   if(translate(aligned,16,store,vu0_physical)){
    if(vu0_physical>=0x11000000u && vu0_physical<=0x11000FF0u){
     vu0_last_qoffset=vu0_physical-0x11000000u;
     p=vu0_micro+vu0_last_qoffset;
     if(store)++vu0_micro_qwrites;else ++vu0_micro_qreads;
    }else if(vu0_physical>=0x11004000u && vu0_physical<=0x11004FF0u){
     vu0_last_qoffset=vu0_physical-0x11004000u;
     p=reinterpret_cast<unsigned char*>(vu0_data)+vu0_last_qoffset;
     if(store)++vu0_data_qwrites;else ++vu0_data_qreads;
    }
   }
  }
  if(!p)return memoryHalt(aligned,16,store,false);''')
change(p,'fprintf(f,"VU1 micro 16KiB SD_WRITES=', 'fprintf(f,"VU0 EE 128-bit memory MICRO_SQ=%llu MICRO_LQ=%llu DATA_SQ=%llu DATA_LQ=%llu LAST_OFFSET=%04X MICRO[0]=%02X,%02X,%02X,%02X\\n",(unsigned long long)vu0_micro_qwrites,(unsigned long long)vu0_micro_qreads,(unsigned long long)vu0_data_qwrites,(unsigned long long)vu0_data_qreads,vu0_last_qoffset,vu0_micro[0],vu0_micro[1],vu0_micro[2],vu0_micro[3]);\n fprintf(f,"VU1 micro 16KiB SD_WRITES=')
change(root/"source/emu_ui.inc","BUILD 059 - MEMORY INVENTORY","BUILD 060 - VU0 RAM")
print("Build 060 exact VU0 128-bit memory backing applied")
