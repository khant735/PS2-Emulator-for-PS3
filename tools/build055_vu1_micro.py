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
# Locate the existing 8-byte handler's unmapped-memory guard, not the 16-byte handler.
s=p.read_text()
anchors=["  if(!p)return memoryHalt(aligned,8,store,false);","  if(!p)return memoryHalt(addr,8,store,false);"]
matches=[a for a in anchors if s.count(a)==1]
if len(matches)!=1:raise SystemExit("Build 055: cannot uniquely identify 8-byte memory handler; refusing unsafe patch")
a=matches[0]
change(p,a,'''  // VU1 microprogram RAM: 0x11008000-0x1100BFFF, distinct from data RAM.
  uint32_t vu1_micro_physical=0;
  if(!p && translate(aligned,8,store,vu1_micro_physical) &&
     vu1_micro_physical>=0x11008000u && vu1_micro_physical<=0x1100BFF8u){
   vu1_micro_last_offset=vu1_micro_physical-0x11008000u;
   p=vu1_micro+vu1_micro_last_offset;
   if(store)++vu1_micro_writes;else ++vu1_micro_reads;
  }
'''+a)
change(p,'fprintf(f,"VU1 data 16KiB SQ_WRITES=', 'fprintf(f,"VU1 micro 16KiB SD_WRITES=%llu LD_READS=%llu LAST_OFFSET=%04X DATA[0]=%02X,%02X,%02X,%02X,%02X,%02X,%02X,%02X\\n",(unsigned long long)vu1_micro_writes,(unsigned long long)vu1_micro_reads,vu1_micro_last_offset,vu1_micro[0],vu1_micro[1],vu1_micro[2],vu1_micro[3],vu1_micro[4],vu1_micro[5],vu1_micro[6],vu1_micro[7]);\n fprintf(f,"VU1 data 16KiB SQ_WRITES=')
change(root/"source/emu_ui.inc","BUILD 054 - VU1 DATA RAM","BUILD 055 - VU1 MICRO RAM")
print("Build 055 VU1 microprogram memory mapping applied")
