#!/usr/bin/env python3
"""Build 057: capture 128-bit VIF1 FIFO ingress at physical 0x10005000."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 057 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t vif1_regs[15];","uint64_t vif1_fifo_qwords,vif1_fifo_last_lo,vif1_fifo_last_hi;uint32_t vif1_regs[15];")
p=root/"source/emu_core.cpp"
change(p,"memset(vif1_regs,0,sizeof(vif1_regs));","vif1_fifo_qwords=vif1_fifo_last_lo=vif1_fifo_last_hi=0;memset(vif1_regs,0,sizeof(vif1_regs));")
# The earlier GIF FIFO handler already uses the sentinel (unsigned char*)1
# to prevent normal RAM writes. Reuse that existing safe dispatch mechanism.
change(p,"  if(!p)return memoryHalt(aligned,16,store,false);",'''  // VIF1 FIFO at physical 0x10005000 accepts 128-bit SQ ingress.
  // Capture only: no VIF command interpreter, FIFO drain, DMA or IRQ.
  if(!p && store){
   uint32_t vif1_fifo_physical=0;
   if(translate(aligned,16,true,vif1_fifo_physical) &&
      vif1_fifo_physical==0x10005000u){
    vif1_fifo_last_lo=rt?reg[rt]:0;
    vif1_fifo_last_hi=rt?reg_hi[rt]:0;
    ++vif1_fifo_qwords;
    p=(unsigned char*)1; // Existing GIF FIFO sentinel skips normal RAM write.
   }
  }
  if(!p)return memoryHalt(aligned,16,store,false);''')
change(p,'fprintf(f,"VIF1 register subset (no FIFO/DMA/IRQ):', 'fprintf(f,"VIF1 FIFO ingress (capture only; no VIF parsing/DMA/IRQ): QWORDS=%llu LAST_LO=%016llX LAST_HI=%016llX\\n",(unsigned long long)vif1_fifo_qwords,(unsigned long long)vif1_fifo_last_lo,(unsigned long long)vif1_fifo_last_hi);\n fprintf(f,"VIF1 register subset (no FIFO/DMA/IRQ):')
change(root/"source/emu_ui.inc","BUILD 056 - VIF1 REGISTERS","BUILD 057 - VIF1 FIFO INGRESS")
print("Build 057 VIF1 FIFO ingress capture applied")
