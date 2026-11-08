#!/usr/bin/env python3
"""Build 041: capture 128-bit GIF FIFO ingress without pretending to render GIF packets."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h";s=h.read_text()
a="uint32_t gif_mode,gif_pause;uint64_t gif_resets;"
b="uint32_t gif_mode,gif_pause;uint64_t gif_resets,gif_fifo_qwords;uint64_t gif_fifo_last_lo,gif_fifo_last_hi;"
assert s.count(a)==1;s=s.replace(a,b);h.write_text(s)
p=root/"source/emu_core.cpp";s=p.read_text()
a="gif_mode=gif_pause=0;gif_resets=0;"
b="gif_mode=gif_pause=0;gif_resets=gif_fifo_qwords=0;gif_fifo_last_lo=gif_fifo_last_hi=0;"
assert s.count(a)==1;s=s.replace(a,b)
a='''  if(!p)return memoryHalt(aligned,16,store,false);
  if(store){uint64_t lower=rt?reg[rt]:0,upper=rt?reg_hi[rt]:0;'''
b='''  // GIF FIFO at physical 0x10006000 accepts 128-bit ingress writes.
  // Capture only: GIF tag parsing, DMA, arbitration and GS rendering are absent.
  if(!p&&store){
   uint32_t physical=0;
   if(translate(aligned,16,true,physical)&&physical==0x10006000u){
    gif_fifo_last_lo=rt?reg[rt]:0;
    gif_fifo_last_hi=rt?reg_hi[rt]:0;
    gif_fifo_qwords++;
    goto completed_quadword;
   }
  }
  if(!p)return memoryHalt(aligned,16,store,false);
  if(store){uint64_t lower=rt?reg[rt]:0,upper=rt?reg_hi[rt]:0;'''
assert s.count(a)==1;s=s.replace(a,b)
# Avoid goto across initialized variables by using an explicit boolean and enclosing normal access.
s=s.replace('''    goto completed_quadword;
''','''    p=(unsigned char*)1; // Sentinel: recognized FIFO, handled below.
''')
s=s.replace('''  if(store){uint64_t lower=rt?reg[rt]:0,upper=rt?reg_hi[rt]:0;
   for(unsigned i=0;i<8;i++){p[i]=(lower>>(8*i))&255;p[i+8]=(upper>>(8*i))&255;}
''','''  if(store){uint64_t lower=rt?reg[rt]:0,upper=rt?reg_hi[rt]:0;
   if(p!=(unsigned char*)1)
    for(unsigned i=0;i<8;i++){p[i]=(lower>>(8*i))&255;p[i+8]=(upper>>(8*i))&255;}
''')
a='''fprintf(f,"GIF control subset (no packets/DMA/rendering): MODE=%08X PAUSE=%u STAT=%08X RESETS=%llu\\n",gif_mode,unsigned(gif_pause!=0),gif_mode|gif_pause,(unsigned long long)gif_resets);'''
b=a+'''
 fprintf(f,"GIF FIFO ingress (capture only; no packets/DMA/rendering): QWORDS=%llu LAST_LO=%016llX LAST_HI=%016llX\\n",
  (unsigned long long)gif_fifo_qwords,(unsigned long long)gif_fifo_last_lo,(unsigned long long)gif_fifo_last_hi);'''
assert s.count(a)==1;s=s.replace(a,b);p.write_text(s)
ui=root/"source/emu_ui.inc";s=ui.read_text();a="BUILD 040 - DVE COMMAND 81";assert s.count(a)==1;ui.write_text(s.replace(a,"BUILD 041 - GIF FIFO INGRESS"))
print("Build 041 GIF FIFO capture applied")
