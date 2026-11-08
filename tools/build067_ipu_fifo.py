#!/usr/bin/env python3
"""Build 067: capture 128-bit IPU input FIFO ingress at 0x10007010."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 067 anchor mismatch {path}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t ipu_regs[4];","uint64_t ipu_fifo_qwords,ipu_fifo_last_lo,ipu_fifo_last_hi;uint32_t ipu_regs[4];")
p=root/"source/emu_core.cpp"
change(p,"memset(ipu_regs,0,sizeof(ipu_regs));","ipu_fifo_qwords=ipu_fifo_last_lo=ipu_fifo_last_hi=0;memset(ipu_regs,0,sizeof(ipu_regs));")
change(p,"  // VIF0 FIFO at physical 0x10004000 accepts 128-bit SQ ingress.",'''  // IPU input FIFO at physical 0x10007010 accepts 128-bit SQ ingress.
  // Diagnostic capture only; no MPEG decoding, DMA, or FIFO drain.
  if(!p && store){
   uint32_t ipu_fifo_physical=0;
   if(translate(aligned,16,true,ipu_fifo_physical) &&
      ipu_fifo_physical==0x10007010u){
    ipu_fifo_last_lo=rt?reg[rt]:0;
    ipu_fifo_last_hi=rt?reg_hi[rt]:0;
    ++ipu_fifo_qwords;
    p=(unsigned char*)1; // Existing FIFO sentinel avoids normal RAM writes.
   }
  }
  // VIF0 FIFO at physical 0x10004000 accepts 128-bit SQ ingress.''')
change(p,'fprintf(f,"IPU register capture (', 'fprintf(f,"IPU input FIFO ingress (capture only; no decode/DMA): QWORDS=%llu LAST_LO=%016llX LAST_HI=%016llX\\n",(unsigned long long)ipu_fifo_qwords,(unsigned long long)ipu_fifo_last_lo,(unsigned long long)ipu_fifo_last_hi);\n fprintf(f,"IPU register capture (')
change(root/"source/emu_ui.inc","BUILD 066 - IPU REGISTERS","BUILD 067 - IPU INPUT FIFO")
print("Build 067 IPU input FIFO capture applied")
