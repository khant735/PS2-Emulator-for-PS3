#!/usr/bin/env python3
"""Build 144: diagnose IOP writes to 1FA00000 without inventing hardware behavior."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h"; c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1: raise SystemExit(f"Build144 anchor mismatch {p.name}: {a[:80]!r} ({s.count(a)})")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_sb_writes,iop_sb_ram_writes,iop_sb_2070_writes;",
"""uint64_t iop_1fa0_attempts;
 uint32_t iop_1fa0_pc,iop_1fa0_insn,iop_1fa0_va,iop_1fa0_pa,iop_1fa0_value;
 uint32_t iop_1fa0_rs,iop_1fa0_rt,iop_1fa0_ra,iop_1fa0_sp,iop_1fa0_next;
 uint64_t iop_sb_writes,iop_sb_ram_writes,iop_sb_2070_writes;""")
patch(c,"iop_sb_writes=iop_sb_ram_writes=iop_sb_2070_writes=0;",
"""iop_1fa0_attempts=0;
 iop_1fa0_pc=iop_1fa0_insn=iop_1fa0_va=iop_1fa0_pa=iop_1fa0_value=0;
 iop_1fa0_rs=iop_1fa0_rt=iop_1fa0_ra=iop_1fa0_sp=iop_1fa0_next=0;
 iop_sb_writes=iop_sb_ram_writes=iop_sb_2070_writes=0;""")
patch(c,'iop_sb_reject=2;\n   snprintf(iop_stop_reason',
"""if((pa&0xffff0000u)==0x1fa00000u){
    ++iop_1fa0_attempts;
    iop_1fa0_pc=addr;iop_1fa0_insn=ins;
    iop_1fa0_va=va;iop_1fa0_pa=pa;iop_1fa0_value=value;
    iop_1fa0_rs=iop_gpr[rs];iop_1fa0_rt=iop_gpr[rt];
    iop_1fa0_ra=iop_gpr[31];iop_1fa0_sp=iop_gpr[29];
    iop_1fa0_next=old_next;
   }
   iop_sb_reject=2;
   snprintf(iop_stop_reason""")
patch(c,'fprintf(f,"BUILD 135 IOP SB:', '''fprintf(f,"BUILD 144 IOP 1FA0 ACCESS: ATTEMPTS=%llu PC=%08X INSN=%08X VA=%08X PA=%08X BYTE=%02X RS_VALUE=%08X RT_VALUE=%08X RA=%08X SP=%08X NEXT=%08X (diagnostic only; unmapped write rejected)\\n",
 (unsigned long long)iop_1fa0_attempts,iop_1fa0_pc,iop_1fa0_insn,iop_1fa0_va,iop_1fa0_pa,
 iop_1fa0_value,iop_1fa0_rs,iop_1fa0_rt,iop_1fa0_ra,iop_1fa0_sp,iop_1fa0_next);
 fprintf(f,"BUILD 135 IOP SB:''')
print("Build144: strict IOP 1FA0 write diagnostics installed")
