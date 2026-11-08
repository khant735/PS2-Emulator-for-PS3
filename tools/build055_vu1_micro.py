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
# The eight-byte access goes through the generic EE load/store path.
# Find exactly one existing 8-byte size test and attach the mapping there.
s=p.read_text()
lines=s.splitlines()
for i,line in enumerate(lines):
 if any(x in line for x in ('memoryHalt(', 'size==8', 'size == 8', 'writeMem(', 'readMem(')):
  print("BUILD055_MEMORY_CONTEXT",i+1,repr(line[:260]))
raise SystemExit("Build 055 diagnostics: inspect generic 8-byte load/store path above")
change(p,'fprintf(f,"VU1 data 16KiB SQ_WRITES=', 'fprintf(f,"VU1 micro 16KiB SD_WRITES=%llu LD_READS=%llu LAST_OFFSET=%04X DATA[0]=%02X,%02X,%02X,%02X,%02X,%02X,%02X,%02X\\n",(unsigned long long)vu1_micro_writes,(unsigned long long)vu1_micro_reads,vu1_micro_last_offset,vu1_micro[0],vu1_micro[1],vu1_micro[2],vu1_micro[3],vu1_micro[4],vu1_micro[5],vu1_micro[6],vu1_micro[7]);\n fprintf(f,"VU1 data 16KiB SQ_WRITES=')
change(root/"source/emu_ui.inc","BUILD 054 - VU1 DATA RAM","BUILD 055 - VU1 MICRO RAM")
print("Build 055 VU1 microprogram memory mapping applied")
