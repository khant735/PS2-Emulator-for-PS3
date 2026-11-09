#!/usr/bin/env python3
"""Build 093: correct IOP memory-control classification and implement signed ADDI."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build093 anchor {p.name}: {a[:90]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(c,"// PS1-compatible IOP DMA channel 0 (MDEC in) MADR.","// PS1-compatible IOP memory-control BIOS ROM delay/size register (0x1F801010).")
patch(c,"// Reset-only diagnostic storage; no DMA execution or transfer effects.","// Provisional reset readback of zero; memory timing/size semantics not yet modeled.")
patch(c,"BUILD 092 IOP DMA CH0 MADR:","BUILD 093 IOP MEMORY CONTROL 1010:")
patch(c,"(reset-only diagnostic; DMA effects unimplemented)","(provisional zero; memory timing effects unimplemented)")
patch(c,"else if(op==9)iop_gpr[rt]=iop_gpr[rs]+(uint32_t)imm;",'''else if(op==8){ // ADDI: signed add, trap on overflow (exception delivery pending).
  int64_t sum=(int64_t)(int32_t)iop_gpr[rs]+(int64_t)imm;
  if(sum>2147483647LL||sum<(-2147483647LL-1LL)){
   snprintf(iop_reason,sizeof(iop_reason),"IOP ADDI overflow PC=%08X OP=%08X",iop_pc,insn);
   iop_running=false;return;
  }
  if(rt)iop_gpr[rt]=(uint32_t)(int32_t)sum;
 }
 else if(op==9)iop_gpr[rt]=iop_gpr[rs]+(uint32_t)imm;''')
patch(u,"BUILD 092 - IOP DMA","BUILD 093 - IOP ADDI")
print("Build 093 IOP ADDI and 0x1F801010 memory-control correction applied")
