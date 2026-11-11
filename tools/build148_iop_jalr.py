#!/usr/bin/env python3
"""Build 148: IOP R3000 JALR with explicit target/link diagnostics."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build148 anchor mismatch {p.name}: {a[:90]!r} ({s.count(a)})")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_lhu_reads,iop_lhu_ram_reads,iop_lhu_rom_reads,iop_lhu_spu2_reads;",
"""uint64_t iop_jalr_count;uint32_t iop_jalr_pc,iop_jalr_target,iop_jalr_link,iop_jalr_rd;
 uint64_t iop_lhu_reads,iop_lhu_ram_reads,iop_lhu_rom_reads,iop_lhu_spu2_reads;""")
patch(c,"iop_lhu_reads=iop_lhu_ram_reads=iop_lhu_rom_reads=iop_lhu_spu2_reads=0;",
"""iop_jalr_count=0;iop_jalr_pc=iop_jalr_target=iop_jalr_link=iop_jalr_rd=0;
 iop_lhu_reads=iop_lhu_ram_reads=iop_lhu_rom_reads=iop_lhu_spu2_reads=0;""")
patch(c,"else if(op==0&&fn==8){branch=true;new_next=iop_gpr[rs];}",
"""else if(op==0&&fn==8){branch=true;new_next=iop_gpr[rs];}
 else if(op==0&&fn==9){ // JALR rd,rs: target read before link register write
  const uint32_t target=iop_gpr[rs];
  const uint32_t link=old_next+4u;
  if(target&3u){
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),
    "IOP JALR unaligned PC=%08X TARGET=%08X",addr,target);
   iop_running=false;return false;
  }
  branch=true;new_next=target;
  if(rd)iop_gpr[rd]=link;
  ++iop_jalr_count;iop_jalr_pc=addr;iop_jalr_target=target;
  iop_jalr_link=link;iop_jalr_rd=rd;
 }""")
patch(c,'fprintf(f,"BUILD 147 IOP LHU:', '''fprintf(f,"BUILD 148 IOP JALR: EXECUTED=%llu LAST_PC=%08X TARGET=%08X LINK=%08X RD=%u (R3000 branch delay; target captured before link write; no SIF side effects)\\n",
 (unsigned long long)iop_jalr_count,iop_jalr_pc,iop_jalr_target,iop_jalr_link,iop_jalr_rd);
 fprintf(f,"BUILD 147 IOP LHU:''')
print("Build148: IOP JALR and branch-target diagnostics installed")
