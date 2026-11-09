#!/usr/bin/env python3
"""Build 089: IOP SW decoder-path and effective-address diagnostics."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build089 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_instructions,iop_sw_writes;","uint64_t iop_instructions,iop_sw_writes,iop_sw_handler_entries,iop_decode_attempts;uint32_t iop_decode_pc,iop_decode_opcode,iop_decode_op,iop_decode_rs,iop_decode_rt,iop_decode_imm,iop_sw_reject_code;")
patch(c,"iop_instructions=iop_sw_writes=0;","iop_instructions=iop_sw_writes=iop_sw_handler_entries=iop_decode_attempts=0;iop_decode_pc=iop_decode_opcode=iop_decode_op=iop_decode_rs=iop_decode_rt=iop_decode_imm=iop_sw_reject_code=0;")
patch(c,"uint32_t old_next=iop_next,new_next=old_next+4;","""++iop_decode_attempts;iop_decode_pc=addr;iop_decode_opcode=ins;iop_decode_op=op;iop_decode_rs=rs;iop_decode_rt=rt;iop_decode_imm=ins&65535u;
 uint32_t old_next=iop_next,new_next=old_next+4;""")
patch(c,"else if(op==43){ // R3000 SW: validate alignment, physical mapping, and RAM bounds","else if(op==43){ // R3000 SW: validate alignment, physical mapping, and RAM bounds\n  ++iop_sw_handler_entries;")
patch(c,'if(va&3u){snprintf(iop_stop_reason', 'if(va&3u){iop_sw_reject_code=1;snprintf(iop_stop_reason')
patch(c,'if(pa>IOP_RAM||IOP_RAM-pa<4u){','if(pa>IOP_RAM||IOP_RAM-pa<4u){iop_sw_reject_code=2;')
patch(c,'++iop_sw_writes;','++iop_sw_writes;iop_sw_reject_code=0;')
patch(c,'fprintf(f,"BUILD 088 IOP SW:', '''fprintf(f,"BUILD 089 IOP DECODE: ATTEMPTS=%llu PC=%08X INSN=%08X OP=%u RS=%u RT=%u IMM=%04X SW_HANDLER_ENTRIES=%llu SW_REJECT=%u (0=none 1=unaligned 2=unmapped)\\n",
 (unsigned long long)iop_decode_attempts,iop_decode_pc,iop_decode_opcode,iop_decode_op,iop_decode_rs,iop_decode_rt,iop_decode_imm,
 (unsigned long long)iop_sw_handler_entries,iop_sw_reject_code);
 fprintf(f,"BUILD 088 IOP SW:''')
patch(u,"BUILD 088 - IOP SW DIAGNOSTICS","BUILD 089 - IOP DECODE DIAGNOSTICS")
print("Build 089 IOP decoder diagnostics applied")
