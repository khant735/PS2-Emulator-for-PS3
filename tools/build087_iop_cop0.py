#!/usr/bin/env python3
"""Build 087: diagnostic IOP COP0 MFC0/MTC0 and reset-register state."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build087 anchor {p.name}: {a[:70]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint32_t iop_pc,iop_next,iop_gpr[32],iop_hi,iop_lo,iop_last_opcode;",
      "uint32_t iop_pc,iop_next,iop_gpr[32],iop_cop0[32],iop_hi,iop_lo,iop_last_opcode;")
patch(c,"memset(iop_gpr,0,sizeof(iop_gpr));iop_pc=",
      "memset(iop_gpr,0,sizeof(iop_gpr));memset(iop_cop0,0,sizeof(iop_cop0));\n iop_cop0[12]=0x00400000u; /* BEV reset state; other COP0 registers provisional */\n iop_pc=")
patch(c,"else if(op==15)iop_gpr[rt]=ins<<16;",
      """else if(op==16&&rs==0){ // IOP R3000 MFC0, including first BIOS instruction at BFC00000
  iop_gpr[rt]=iop_cop0[rd];
 }
 else if(op==16&&rs==4){ // MTC0 diagnostic register storage; side effects not emulated
  iop_cop0[rd]=iop_gpr[rt];
 }
 else if(op==15)iop_gpr[rt]=ins<<16;""")
patch(c,'fprintf(f,"BUILD 086 IOP BOOTSTRAP: PC=', 'fprintf(f,"BUILD 087 IOP COP0: PRID=%08X STATUS=%08X CAUSE=%08X EPC=%08X (provisional COP0 model; no exceptions)\\n",iop_cop0[15],iop_cop0[12],iop_cop0[13],iop_cop0[14]);\n fprintf(f,"BUILD 086 IOP BOOTSTRAP: PC=')
patch(u,"BUILD 086 - IOP BOOTSTRAP","BUILD 087 - IOP COP0")
print("Build 087 IOP COP0 diagnostic patch applied")
