#!/usr/bin/env python3
"""Build 045: structured EE DMAC MMIO diagnostic register storage.
No DMA transfer, scheduling, completion or interrupt generation.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build 045 anchor mismatch {path}: {old[:100]!r} count={s.count(old)}")
 path.write_text(s.replace(old,new,1))
h=root/"include/emu_core.h"
change(h,"uint32_t vif0_dma_80;uint64_t vif0_dma_80_writes,vif0_dma_80_reads;",
"""uint32_t dmac_channel_regs[10][7],dmac_global_regs[6];
 uint64_t dmac_channel_writes[10],dmac_channel_reads[10],dmac_global_writes,dmac_global_reads;""")
p=root/"source/emu_core.cpp"
change(p,"vif0_dma_80=0;vif0_dma_80_writes=vif0_dma_80_reads=0;",
"""memset(dmac_channel_regs,0,sizeof(dmac_channel_regs));memset(dmac_global_regs,0,sizeof(dmac_global_regs));
 memset(dmac_channel_writes,0,sizeof(dmac_channel_writes));memset(dmac_channel_reads,0,sizeof(dmac_channel_reads));
 dmac_global_writes=dmac_global_reads=0;""")
# Exact register address lookup, avoiding acceptance of holes in channel address ranges.
decoder="""static const uint32_t dma_bases[10]={0x10008000u,0x10009000u,0x1000A000u,0x1000B000u,0x1000B400u,0x1000C000u,0x1000C400u,0x1000C800u,0x1000D000u,0x1000D400u};
 static const uint32_t dma_offsets[7]={0x00u,0x10u,0x20u,0x30u,0x40u,0x50u,0x80u};
"""
read="""if(size==4){
""" + decoder + """ for(unsigned c=0;c<10;++c)for(unsigned r=0;r<7;++r){
   // +0x80 is a diagnostic-only channel slot, not an asserted CHCR alias.
   if(p==dma_bases[c]+dma_offsets[r]){v=dmac_channel_regs[c][r];++dmac_channel_reads[c];return true;}
  }
  if(p>=0x1000E000u && p<=0x1000E050u && ((p-0x1000E000u)%0x10u)==0){
   unsigned r=(p-0x1000E000u)/0x10u;v=dmac_global_regs[r];++dmac_global_reads;return true;
  }
 }
"""
write="""if(size==4){
""" + decoder + """ for(unsigned c=0;c<10;++c)for(unsigned r=0;r<7;++r){
   if(p==dma_bases[c]+dma_offsets[r]){
    // Store the written CHCR value but do not start DMA or synthesize completion.
    dmac_channel_regs[c][r]=uint32_t(v);++dmac_channel_writes[c];return true;
   }
  }
  if(p>=0x1000E000u && p<=0x1000E050u && ((p-0x1000E000u)%0x10u)==0){
   unsigned r=(p-0x1000E000u)/0x10u;dmac_global_regs[r]=uint32_t(v);++dmac_global_writes;return true;
  }
 }
"""
change(p,"if(p==0x10008080u){v=vif0_dma_80;++vif0_dma_80_reads;return true;}",read.rstrip())
change(p,"if(size==4 && p==0x10008080u){vif0_dma_80=uint32_t(v);++vif0_dma_80_writes;return true;}",write.rstrip())
change(p,'fprintf(f,"VIF0 DMA block +80 diagnostic storage (no DMA/IRQ): VALUE=%08X WRITES=%llu READS=%llu\\n",vif0_dma_80,(unsigned long long)vif0_dma_80_writes,(unsigned long long)vif0_dma_80_reads);',
'''fprintf(f,"EE DMAC register storage only (no transfers/IRQ): GLOBAL_WRITES=%llu GLOBAL_READS=%llu\\n",(unsigned long long)dmac_global_writes,(unsigned long long)dmac_global_reads);
 for(int i=0;i<10;++i)fprintf(f,"DMAC CH%u CHCR=%08X MADR=%08X QWC=%08X TADR=%08X ASR0=%08X ASR1=%08X AUX80=%08X WRITES=%llu READS=%llu\\n",unsigned(i),dmac_channel_regs[i][0],dmac_channel_regs[i][1],dmac_channel_regs[i][2],dmac_channel_regs[i][3],dmac_channel_regs[i][4],dmac_channel_regs[i][5],dmac_channel_regs[i][6],(unsigned long long)dmac_channel_writes[i],(unsigned long long)dmac_channel_reads[i]);
 for(int i=0;i<6;++i)fprintf(f,"DMAC GLOBAL +%02X=%08X\\n",unsigned(i*16),dmac_global_regs[i]);''')
change(root/"source/emu_ui.inc","BUILD 044 - VIF0 DMA DIAGNOSTICS","BUILD 045 - EE DMAC REGISTERS")
print("Build 045 structured DMAC diagnostic register patch applied")
