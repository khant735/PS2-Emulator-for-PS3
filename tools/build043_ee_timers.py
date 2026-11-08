#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build 043 anchor mismatch {path}: {old[:80]!r}, found {s.count(old)}")
 path.write_text(s.replace(old,new,1))
h=root/"include/emu_core.h"
change(h,"uint32_t dmac_ctrl;uint64_t dmac_ctrl_writes,dmac_ctrl_reads;","uint32_t ee_timer_count[4],ee_timer_mode[4],ee_timer_comp[4],ee_timer_hold[4];uint64_t ee_timer_writes,ee_timer_reads;")
p=root/"source/emu_core.cpp"
change(p,"dmac_ctrl=0;dmac_ctrl_writes=dmac_ctrl_reads=0;","for(int i=0;i<4;++i){ee_timer_count[i]=ee_timer_mode[i]=ee_timer_comp[i]=ee_timer_hold[i]=0;}ee_timer_writes=ee_timer_reads=0;")
change(p,"if(p==0x10000010u){v=dmac_ctrl;++dmac_ctrl_reads;return true;}","""if(p>=0x10000000u && p<0x10002000u){
 unsigned t=(p-0x10000000u)/0x800u, off=(p-0x10000000u)%0x800u;
 if(t<4 && (off==0 || off==0x10 || off==0x20 || (off==0x30 && t<2))){
 v=(off==0?ee_timer_count[t]:off==0x10?ee_timer_mode[t]:off==0x20?ee_timer_comp[t]:ee_timer_hold[t]);
 ++ee_timer_reads;return true;
 }
 }""")
change(p,"if(size==4&&p==0x10000010u){dmac_ctrl=uint32_t(v);++dmac_ctrl_writes;return true;}","""if(size==4 && p>=0x10000000u && p<0x10002000u){
 unsigned t=(p-0x10000000u)/0x800u, off=(p-0x10000000u)%0x800u;
 if(t<4 && (off==0 || off==0x10 || off==0x20 || (off==0x30 && t<2))){
 if(off==0)ee_timer_count[t]=uint32_t(v);
 else if(off==0x10){ee_timer_mode[t]=uint32_t(v);ee_timer_count[t]=0;}
 else if(off==0x20)ee_timer_comp[t]=uint32_t(v);
 else ee_timer_hold[t]=uint32_t(v);
 ++ee_timer_writes;return true;
 }
 }""")
change(p,'fprintf(f,"EE DMAC D_CTRL storage only (no DMA/IRQ): CTRL=%08X WRITES=%llu READS=%llu\\n",dmac_ctrl,(unsigned long long)dmac_ctrl_writes,(unsigned long long)dmac_ctrl_reads);','''fprintf(f,"EE timers storage-only (no clock/IRQ): WRITES=%llu READS=%llu\\n",(unsigned long long)ee_timer_writes,(unsigned long long)ee_timer_reads);
 for(int t=0;t<4;++t)fprintf(f,"EE TIMER%d COUNT=%08X MODE=%08X COMP=%08X HOLD=%08X\\n",t,ee_timer_count[t],ee_timer_mode[t],ee_timer_comp[t],ee_timer_hold[t]);''')
change(root/"source/emu_ui.inc","BUILD 042 - EE DMAC CONTROL","BUILD 043 - EE TIMER REGISTERS")
print("Build 043 EE timers applied")
