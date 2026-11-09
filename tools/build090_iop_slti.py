#!/usr/bin/env python3
"""Build 090: implement IOP SLTI and log reset-vector ROM words."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build090 anchor {p.name}: {a[:80]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_instructions,iop_sw_writes,iop_sw_handler_entries,iop_decode_attempts;","uint64_t iop_instructions,iop_sw_writes,iop_sw_handler_entries,iop_decode_attempts,iop_slti_executed;")
patch(c,"iop_sw_handler_entries=iop_decode_attempts=0;","iop_sw_handler_entries=iop_decode_attempts=iop_slti_executed=0;")
patch(c,"else if(op==9)iop_gpr[rt]=iop_gpr[rs]+(uint32_t)imm;","else if(op==9)iop_gpr[rt]=iop_gpr[rs]+(uint32_t)imm;\n else if(op==10){iop_gpr[rt]=((int32_t)iop_gpr[rs]<imm)?1u:0u;++iop_slti_executed;} // R3000 SLTI signed comparison")
patch(c,'fprintf(f,"BUILD 089 IOP DECODE:', '''fprintf(f,"BUILD 090 IOP SLTI: EXECUTED=%llu ROM_RESET_WORDS=%08X,%08X,%08X,%08X (little-endian ROM bytes; no synthetic boot data)\\n",
 (unsigned long long)iop_slti_executed,le32(rom),le32(rom+4),le32(rom+8),le32(rom+12));
 fprintf(f,"BUILD 089 IOP DECODE:''')
patch(u,"BUILD 089 - IOP DECODE DIAGNOSTICS","BUILD 090 - IOP SLTI")
print("Build 090 IOP SLTI and ROM diagnostics applied")
