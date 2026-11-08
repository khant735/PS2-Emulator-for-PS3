#!/usr/bin/env python3
"""Build 055: map VU1 microprogram RAM for EE 64-bit memory operations."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 055 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"unsigned char vu1_data[16384];","unsigned char vu1_micro[16384];uint64_t vu1_micro_writes,vu1_micro_reads;uint32_t vu1_micro_last_offset;unsigned char vu1_data[16384];")
p=root/"source/emu_core.cpp"
change(p,"memset(vu1_data,0,sizeof(vu1_data));","memset(vu1_micro,0,sizeof(vu1_micro));vu1_micro_writes=vu1_micro_reads=0;vu1_micro_last_offset=0;memset(vu1_data,0,sizeof(vu1_data));")
# Intercept the EE ordinary 8-byte SD/LD path before the existing MMIO fallback.
# This preserves the 16-byte SQ/LQ code and all other MMIO behavior.
change(p,"  else if(!mmioRead(addr,size,v))return memoryHalt(addr,size,false,false);",'''  else if(size==8 && (uint32_t(addr)>=0x11008000u) && (uint32_t(addr)<=0x1100BFF8u)){
   uint32_t off=uint32_t(addr)-0x11008000u;
   vu1_micro_last_offset=off;v=0;
   for(unsigned i=0;i<8;++i)v|=uint64_t(vu1_micro[off+i])<<(i*8);
   ++vu1_micro_reads;
  }
  else if(!mmioRead(addr,size,v))return memoryHalt(addr,size,false,false);''')
change(p,"  else if(!mmioWrite(addr,size,b))return memoryHalt(addr,size,true,false);",'''  else if(size==8 && (uint32_t(addr)>=0x11008000u) && (uint32_t(addr)<=0x1100BFF8u)){
   uint32_t off=uint32_t(addr)-0x11008000u;
   vu1_micro_last_offset=off;
   for(unsigned i=0;i<8;++i)vu1_micro[off+i]=uint8_t(b>>(i*8));
   ++vu1_micro_writes;
  }
  else if(!mmioWrite(addr,size,b))return memoryHalt(addr,size,true,false);''')
change(p,'fprintf(f,"VU1 data 16KiB SQ_WRITES=', 'fprintf(f,"VU1 micro 16KiB SD_WRITES=%llu LD_READS=%llu LAST_OFFSET=%04X DATA[0]=%02X,%02X,%02X,%02X,%02X,%02X,%02X,%02X\\n",(unsigned long long)vu1_micro_writes,(unsigned long long)vu1_micro_reads,vu1_micro_last_offset,vu1_micro[0],vu1_micro[1],vu1_micro[2],vu1_micro[3],vu1_micro[4],vu1_micro[5],vu1_micro[6],vu1_micro[7]);\n fprintf(f,"VU1 data 16KiB SQ_WRITES=')
change(root/"source/emu_ui.inc","BUILD 054 - VU1 DATA RAM","BUILD 055 - VU1 MICRO RAM")
print("Build 055 VU1 microprogram memory mapping applied")
