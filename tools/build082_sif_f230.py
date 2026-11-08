#!/usr/bin/env python3
"""Build 082: capture SIF F230 read/write and its subsequent BIOS use."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build 082 anchor mismatch {path}: {old[:70]!r} count={s.count(old)}")
 path.write_text(s.replace(old,new,1))
h=root/"include/emu_core.h"
change(h,"uint32_t ee_sif_f260;","uint32_t ee_sif_f230;uint64_t ee_sif_f230_reads,ee_sif_f230_writes;uint32_t ee_sif_f230_last_pc,ee_sif_f230_last_value;uint32_t ee_sif_f260;")
p=root/"source/emu_core.cpp"
change(p,"ee_sif_f260=0;","ee_sif_f230=0;ee_sif_f230_reads=ee_sif_f230_writes=0;ee_sif_f230_last_pc=ee_sif_f230_last_value=0;ee_sif_f260=0;")
s=p.read_text()
for method,body in [
 ("mmioRead",''' if(size==4 && (a&0x1FFFFFFFu)==0x1000F230u){
  // Experimental storage-only response; no IOP handshake or status synthesis.
  v=ee_sif_f230;++ee_sif_f230_reads;ee_sif_f230_last_pc=pc;return true;
 }
'''),
 ("mmioWrite",''' if(size==4 && (a&0x1FFFFFFFu)==0x1000F230u){
  ee_sif_f230=uint32_t(v);++ee_sif_f230_writes;
  ee_sif_f230_last_pc=pc;ee_sif_f230_last_value=uint32_t(v);return true;
 }
''')]:
 pattern=r"(bool\s+Core::"+method+r"\s*\([^)]*\)\s*\{)"
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build 082 method missing {method}: {len(matches)}")
 m=matches[0];s=s[:m.end()]+"\n"+body+s[m.end():]
p.write_text(s)
change(p,'fprintf(f,"EE SDL/SDR little-endian stores:', 'fprintf(f,"EE SIF 1000F230 diagnostic latch (unverified reset value=0; no IOP effects): VALUE=%08X READS=%llu WRITES=%llu LAST_PC=%08X LAST_WRITE=%08X\\n",ee_sif_f230,(unsigned long long)ee_sif_f230_reads,(unsigned long long)ee_sif_f230_writes,ee_sif_f230_last_pc,ee_sif_f230_last_value);\n fprintf(f,"EE SDL/SDR little-endian stores:')
change(root/"source/emu_ui.inc","BUILD 081 - EE SIF F2XX","BUILD 082 - EE SIF F230")
print("Build 082 SIF F230 diagnostic capture applied")
