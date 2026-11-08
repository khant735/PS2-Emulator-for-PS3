#!/usr/bin/env python3
"""Build 042: minimal EE DMAC D_CTRL storage; no transfers or interrupts."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def replace_once(path,old,new):
    text=path.read_text()
    if text.count(old)!=1:
        raise SystemExit(f"Expected exactly one anchor in {path}: {old!r}; found {text.count(old)}")
    path.write_text(text.replace(old,new,1))
h=root/"include/emu_core.h"
replace_once(h,"uint32_t gif_mode,gif_pause;","uint32_t dmac_ctrl;uint64_t dmac_ctrl_writes,dmac_ctrl_reads;uint32_t gif_mode,gif_pause;")
p=root/"source/emu_core.cpp"
replace_once(p,"gif_mode=gif_pause=0;gif_resets=gif_fifo_qwords=0;","dmac_ctrl=0;dmac_ctrl_writes=dmac_ctrl_reads=0;gif_mode=gif_pause=0;gif_resets=gif_fifo_qwords=0;")
replace_once(p," if(size!=4)return false;\n if(p==0x10003020u)"," if(size!=4)return false;\n if(p==0x10000010u){v=dmac_ctrl;++dmac_ctrl_reads;return true;}\n if(p==0x10003020u)")
replace_once(p," // Record the low-page privileged video registers; no display side effects."," if(size==4&&p==0x10000010u){dmac_ctrl=uint32_t(v);++dmac_ctrl_writes;return true;}\n // Record the low-page privileged video registers; no display side effects.")
replace_once(p,'fprintf(f,"GIF control subset','fprintf(f,"EE DMAC D_CTRL storage only (no DMA/IRQ): CTRL=%08X WRITES=%llu READS=%llu\\n",dmac_ctrl,(unsigned long long)dmac_ctrl_writes,(unsigned long long)dmac_ctrl_reads);\n fprintf(f,"GIF control subset')
ui=root/"source/emu_ui.inc"
replace_once(ui,"BUILD 041 - GIF FIFO INGRESS","BUILD 042 - EE DMAC CONTROL")
print("Build 042 DMAC D_CTRL patch applied")
