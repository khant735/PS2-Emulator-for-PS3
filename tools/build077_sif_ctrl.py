#!/usr/bin/env python3
"""Build 077: narrowly scoped EE SIF control register storage and diagnostics."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 077 anchor mismatch {path}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t ee_sdl_count,ee_sdr_count;","uint32_t ee_sif_ctrl;uint64_t ee_sif_ctrl_reads,ee_sif_ctrl_writes;uint32_t ee_sif_ctrl_last_pc,ee_sif_ctrl_last_value;uint64_t ee_sdl_count,ee_sdr_count;")
p=root/"source/emu_core.cpp"
change(p,"ee_sdl_count=ee_sdr_count=0;","ee_sif_ctrl=0;ee_sif_ctrl_reads=ee_sif_ctrl_writes=0;ee_sif_ctrl_last_pc=ee_sif_ctrl_last_value=0;ee_sdl_count=ee_sdr_count=0;")
s=p.read_text()
for method,body in [
 ("mmioRead",''' if(size==4 && a==0x1000F240u){
  // EE SIF control: diagnostic storage only, no IOP handshake/interrupts.
  v=ee_sif_ctrl;++ee_sif_ctrl_reads;ee_sif_ctrl_last_pc=pc;return true;
 }
'''),
 ("mmioWrite",''' if(size==4 && a==0x1000F240u){
  // EE SIF control: experimental register latch, no IOP side effects.
  ee_sif_ctrl=uint32_t(v);++ee_sif_ctrl_writes;
  ee_sif_ctrl_last_pc=pc;ee_sif_ctrl_last_value=uint32_t(v);return true;
 }
''')]:
 pattern=r"(bool\s+Core::"+method+r"\s*\([^)]*\)\s*\{)"
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build 077 cannot locate {method}: {len(matches)}")
 m=matches[0];s=s[:m.end()]+"\n"+body+s[m.end():]
p.write_text(s)
change(p,'fprintf(f,"EE SDL/SDR little-endian stores:', 'fprintf(f,"EE SIF CTRL 1000F240 experimental latch (no IOP handshake): VALUE=%08X READS=%llu WRITES=%llu LAST_PC=%08X LAST_WRITE=%08X\\n",ee_sif_ctrl,(unsigned long long)ee_sif_ctrl_reads,(unsigned long long)ee_sif_ctrl_writes,ee_sif_ctrl_last_pc,ee_sif_ctrl_last_value);\n fprintf(f,"EE SDL/SDR little-endian stores:')
change(root/"source/emu_ui.inc","BUILD 076 - EE SDL/SDR","BUILD 077 - EE SIF CTRL")
print("Build 077 EE SIF control 1000F240 diagnostic latch applied")
