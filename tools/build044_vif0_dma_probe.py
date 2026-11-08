#!/usr/bin/env python3
"""Build 044: narrow VIF0 DMA-block +0x80 MMIO diagnostic latch.
No DMA engine, no interrupts, no invented CHCR behaviour.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,old,new):
 s=path.read_text()
 n=s.count(old)
 if n!=1:raise SystemExit(f"Build 044 anchor mismatch {path}: {old[:110]!r}; found {n}")
 path.write_text(s.replace(old,new,1))
h=root/"include/emu_core.h"
change(h,"uint32_t ee_timer_count[4]","uint32_t vif0_dma_80;uint64_t vif0_dma_80_writes,vif0_dma_80_reads;uint32_t ee_timer_count[4]")
p=root/"source/emu_core.cpp"
change(p,"ee_timer_writes=ee_timer_reads=0;","ee_timer_writes=ee_timer_reads=0;vif0_dma_80=0;vif0_dma_80_writes=vif0_dma_80_reads=0;")
change(p,"if(p>=0x10000000u && p<0x10002000u){","if(p==0x10008080u){v=vif0_dma_80;++vif0_dma_80_reads;return true;}\n if(p>=0x10000000u && p<0x10002000u){")
change(p,"if(size==4 && p>=0x10000000u && p<0x10002000u){","if(size==4 && p==0x10008080u){vif0_dma_80=uint32_t(v);++vif0_dma_80_writes;return true;}\n if(size==4 && p>=0x10000000u && p<0x10002000u){")
change(p,'fprintf(f,"EE timers storage-only','fprintf(f,"VIF0 DMA block +80 diagnostic storage (no DMA/IRQ): VALUE=%08X WRITES=%llu READS=%llu\\n",vif0_dma_80,(unsigned long long)vif0_dma_80_writes,(unsigned long long)vif0_dma_80_reads);\n fprintf(f,"EE timers storage-only')
change(root/"source/emu_ui.inc","BUILD 043 - EE TIMER REGISTERS","BUILD 044 - VIF0 DMA DIAGNOSTICS")
print("Build 044 narrow VIF0 DMA diagnostic patch applied")
