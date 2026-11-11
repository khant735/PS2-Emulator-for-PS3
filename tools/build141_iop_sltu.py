#!/usr/bin/env python3
"""Build 141: R3000A SLTU register instruction (SPECIAL funct 0x2B).

Observed IOP BIOS: BFC02644 0105102B = SLTU v0,a0,a1.
Unsigned 32-bit comparison; no SIF or MMIO side effects.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
c=root/"source/emu_core.cpp"
h=root/"include/emu_core.h"
def once(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build141 anchor mismatch {path.name}: {old!r} count={s.count(old)}")
 path.write_text(s.replace(old,new,1))
once(h,"uint64_t iop_1060_reads,iop_1060_writes;","uint64_t iop_sltu_count;uint32_t iop_sltu_last_pc,iop_sltu_last_result;\n uint64_t iop_1060_reads,iop_1060_writes;")
once(c,"iop_1060_reads=iop_1060_writes=0;","iop_sltu_count=0;iop_sltu_last_pc=iop_sltu_last_result=0;\n iop_1060_reads=iop_1060_writes=0;")
once(c,"else if(op==0&&fn==37)iop_gpr[rd]=iop_gpr[rs]|iop_gpr[rt];",
"""else if(op==0&&fn==37)iop_gpr[rd]=iop_gpr[rs]|iop_gpr[rt];
 else if(op==0&&fn==43){ // R3000 SLTU rd,rs,rt: unsigned 32-bit compare
  const uint32_t result=(iop_gpr[rs]<iop_gpr[rt])?1u:0u;
  iop_gpr[rd]=result;
  ++iop_sltu_count;iop_sltu_last_pc=addr;iop_sltu_last_result=result;
 }""")
once(c,'fprintf(f,"BUILD 140 IOP 1F801060:', '''fprintf(f,"BUILD 141 IOP SLTU: EXECUTED=%llu LAST_PC=%08X LAST_RESULT=%u (unsigned 32-bit comparison; no hardware side effects)\\n",
 (unsigned long long)iop_sltu_count,iop_sltu_last_pc,iop_sltu_last_result);
 fprintf(f,"BUILD 140 IOP 1F801060:''')
print("Build141: IOP SLTU installed")
