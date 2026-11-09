#!/usr/bin/env python3
"""Build 129: observed 8258 diagnostic latch and bounded IOP memory-access history."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build129 anchor {p.name}: {a[:90]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_mmio_8250_reads,iop_mmio_8250_writes;", """uint64_t iop_mmio_8258_reads,iop_mmio_8258_writes;
 uint32_t iop_mmio_8258_value,iop_mmio_8258_last_pc,iop_mmio_8258_last_value;
 uint32_t iop_access_head,iop_access_count;
 uint32_t iop_access_pc[64],iop_access_pa[64],iop_access_va[64],iop_access_value[64];
 unsigned char iop_access_kind[64];
 uint64_t iop_mmio_8250_reads,iop_mmio_8250_writes;""")
patch(c,"iop_mmio_8250_reads=iop_mmio_8250_writes=0;", """iop_mmio_8258_reads=iop_mmio_8258_writes=0;
 iop_mmio_8258_value=iop_mmio_8258_last_pc=iop_mmio_8258_last_value=0;
 iop_access_head=iop_access_count=0;
 memset(iop_access_pc,0,sizeof(iop_access_pc));memset(iop_access_pa,0,sizeof(iop_access_pa));
 memset(iop_access_va,0,sizeof(iop_access_va));memset(iop_access_value,0,sizeof(iop_access_value));
 memset(iop_access_kind,0,sizeof(iop_access_kind));
 iop_mmio_8250_reads=iop_mmio_8250_writes=0;""")
patch(c,"if(pa==0x1f808250u){\n   iop_mmio_8250_value=iop_gpr[rt];", """if(pa==0x1f808258u){
   iop_mmio_8258_value=iop_gpr[rt];
   iop_mmio_8258_last_pc=addr;iop_mmio_8258_last_value=iop_gpr[rt];
   ++iop_mmio_8258_writes;
  }else if(pa==0x1f808250u){
   iop_mmio_8250_value=iop_gpr[rt];""")
patch(c,"&&pa!=0x1f808250u){iop_ram[pa]","&&pa!=0x1f808250u&&pa!=0x1f808258u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f808250u){", """if(!src&&pa==0x1f808258u){
    iop_gpr[rt]=iop_mmio_8258_value;iop_lw_value=iop_gpr[rt];
    ++iop_mmio_8258_reads;++iop_lw_reads;iop_lw_reject=0;
   }else if(!src&&pa==0x1f808250u){""")
# Record SW attempts and LW attempts, including unmapped accesses, before validation.
patch(c,"iop_last_sw_pa=pa;", """iop_last_sw_pa=pa;
  {unsigned n=iop_access_head++&63u;
   iop_access_pc[n]=addr;iop_access_va[n]=va;iop_access_pa[n]=pa;
   iop_access_value[n]=iop_gpr[rt];iop_access_kind[n]='W';
   if(iop_access_count<64u)++iop_access_count;}""")
patch(c,"iop_lw_va=va;iop_lw_pa=pa;", """iop_lw_va=va;iop_lw_pa=pa;
  {unsigned n=iop_access_head++&63u;
   iop_access_pc[n]=addr;iop_access_va[n]=va;iop_access_pa[n]=pa;
   iop_access_value[n]=0;iop_access_kind[n]='R';
   if(iop_access_count<64u)++iop_access_count;}""")
patch(c,'fprintf(f,"BUILD 128 IOP MMIO 8250:', '''fprintf(f,"BUILD 129 IOP MMIO 8258: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch only; no hardware side effects)\\n",
 (unsigned long long)iop_mmio_8258_writes,(unsigned long long)iop_mmio_8258_reads,
 iop_mmio_8258_last_pc,iop_mmio_8258_last_value,iop_mmio_8258_value);
 fprintf(f,"BUILD 129 IOP ACCESS HISTORY: COUNT=%u (last 64 attempted LW/SW; R value not captured)\\n",iop_access_count);
 for(unsigned k=0;k<iop_access_count;++k){
  unsigned n=(iop_access_head-iop_access_count+k)&63u;
  fprintf(f,"IOP ACCESS %02u %c PC=%08X VA=%08X PA=%08X SW_VALUE=%08X\\n",
   k,iop_access_kind[n],iop_access_pc[n],iop_access_va[n],iop_access_pa[n],iop_access_value[n]);
 }
 fprintf(f,"BUILD 128 IOP MMIO 8250:''')
patch(c,"/8248/8250 diagnostic MMIO; other MMIO rejected)","/8248/8250/8258 diagnostic MMIO; other MMIO rejected)")
print("Build129: 8258 latch and 64-entry IOP LW/SW access history installed")
