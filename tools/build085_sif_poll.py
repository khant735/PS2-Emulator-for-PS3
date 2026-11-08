#!/usr/bin/env python3
"""Build 085: focused SIF F230 polling diagnostics (no fabricated handshake)."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h"
c=root/"source/emu_core.cpp"
u=root/"source/emu_ui.inc"
def change(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build 085 anchor mismatch {p.name}: {a[:85]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
change(h,"uint64_t ee_sif_f230_reads,ee_sif_f230_writes;","uint64_t ee_sif_f230_reads,ee_sif_f230_writes;uint64_t ee_sif_f230_first_instruction,ee_sif_f230_last_instruction;uint64_t ee_sif_f230_zero_reads,ee_sif_f230_nonzero_reads;uint64_t ee_sif_f230_poll_pc_5f00,ee_sif_f230_other_pc;")
change(c,"ee_sif_f230_reads=ee_sif_f230_writes=0;","ee_sif_f230_reads=ee_sif_f230_writes=0;ee_sif_f230_first_instruction=ee_sif_f230_last_instruction=0;ee_sif_f230_zero_reads=ee_sif_f230_nonzero_reads=0;ee_sif_f230_poll_pc_5f00=ee_sif_f230_other_pc=0;")
change(c,"v=ee_sif_f230;++ee_sif_f230_reads;ee_sif_f230_last_pc=pc;return true;","""v=ee_sif_f230;
  if(!ee_sif_f230_reads)ee_sif_f230_first_instruction=instructions;
  ee_sif_f230_last_instruction=instructions;
  ++ee_sif_f230_reads;
  if(v==0)++ee_sif_f230_zero_reads;else ++ee_sif_f230_nonzero_reads;
  if(pc==0x80005F00u)++ee_sif_f230_poll_pc_5f00;else ++ee_sif_f230_other_pc;
  ee_sif_f230_last_pc=pc;return true;""")
change(c,'fprintf(f,"EE SDL/SDR little-endian stores:', '''fprintf(f,"BUILD 085 SIF F230 POLL: FIRST_RETIRED=%llu LAST_RETIRED=%llu ZERO_READS=%llu NONZERO_READS=%llu PC_80005F00_READS=%llu OTHER_PC_READS=%llu\\n",
  (unsigned long long)ee_sif_f230_first_instruction,(unsigned long long)ee_sif_f230_last_instruction,
  (unsigned long long)ee_sif_f230_zero_reads,(unsigned long long)ee_sif_f230_nonzero_reads,
  (unsigned long long)ee_sif_f230_poll_pc_5f00,(unsigned long long)ee_sif_f230_other_pc);
 fprintf(f,"BIOS POLL DISASSEMBLY (observed Build 083): 80005EF8=LUI V0,B000; 80005EFC=ORI V0,V0,F230; 80005F00=LW A0,0(V0); 80005F54=LW V0,0(V0); 80005F58=BEQ A0,V0,+1C; 80006310=AND V0,V0,S0; 80006314=BEQ V0,ZERO,-4\\n");
 fprintf(f,"EE SDL/SDR little-endian stores:''')
change(u,"BUILD 084 - EE IPS COUNTER","BUILD 085 - SIF POLL DIAGNOSTICS")
print("Build 085 SIF poll diagnostics applied")
