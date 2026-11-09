#!/usr/bin/env python3
"""Build 092: diagnostic IOP DMA channel-0 MADR read at 1F801010."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build092 anchor {p.name}: {a[:80]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"iop_lw_reject;","iop_lw_reject;uint64_t iop_dma_madr_reads;uint32_t iop_dma_madr_value;")
patch(c,"iop_lw_va=iop_lw_pa=iop_lw_value=iop_lw_reject=0;","iop_lw_va=iop_lw_pa=iop_lw_value=iop_lw_reject=0;iop_dma_madr_reads=0;iop_dma_madr_value=0;")
patch(c,"if(!src){iop_lw_reject=2;",'''if(!src&&pa==0x1f801010u){
    // PS1-compatible IOP DMA channel 0 (MDEC in) MADR.
    // Reset-only diagnostic storage; no DMA execution or transfer effects.
    iop_gpr[rt]=iop_dma_madr_value;iop_lw_value=iop_gpr[rt];
    ++iop_dma_madr_reads;++iop_lw_reads;iop_lw_reject=0;
  }else if(!src){iop_lw_reject=2;''')
patch(c,"iop_gpr[rt]=le32(src);iop_lw_value=iop_gpr[rt];++iop_lw_reads;iop_lw_reject=0;",'''if(src){iop_gpr[rt]=le32(src);iop_lw_value=iop_gpr[rt];++iop_lw_reads;iop_lw_reject=0;}''')
patch(c,'fprintf(f,"BUILD 091 IOP LW:', '''fprintf(f,"BUILD 092 IOP DMA CH0 MADR: READS=%llu VALUE=%08X (reset-only diagnostic; DMA effects unimplemented)\\n",
 (unsigned long long)iop_dma_madr_reads,iop_dma_madr_value);
 fprintf(f,"BUILD 091 IOP LW:''')
patch(u,"BUILD 091 - IOP LW","BUILD 092 - IOP DMA")
print("Build 092 IOP DMA channel 0 MADR diagnostic applied")
