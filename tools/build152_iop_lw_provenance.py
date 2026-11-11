#!/usr/bin/env python3
"""Build 152: trace IOP LW destination provenance without changing guest semantics."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build152 anchor mismatch {p.name}: {a[:90]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_jalr_count;", """uint32_t iop_lw152_head,iop_lw152_count;
 uint32_t iop_lw152_pc[32],iop_lw152_va[32],iop_lw152_val[32],iop_lw152_rt[32];
 uint64_t iop_jalr_count;""")
patch(c,"iop_jalr_count=0;", """iop_lw152_head=iop_lw152_count=0;
 memset(iop_lw152_pc,0,sizeof(iop_lw152_pc));
 memset(iop_lw152_va,0,sizeof(iop_lw152_va));
 memset(iop_lw152_val,0,sizeof(iop_lw152_val));
 memset(iop_lw152_rt,0,sizeof(iop_lw152_rt));
 iop_jalr_count=0;""")
patch(c,"iop_gpr[rt]=le32(src);iop_lw_value=iop_gpr[rt];++iop_lw_reads;iop_lw_reject=0;", """const uint32_t loaded=le32(src);
  {const unsigned slot=iop_lw152_head&31u;
   iop_lw152_pc[slot]=addr;iop_lw152_va[slot]=va;
   iop_lw152_val[slot]=loaded;iop_lw152_rt[slot]=rt;
   iop_lw152_head=(iop_lw152_head+1u)&31u;
   if(iop_lw152_count<32u)++iop_lw152_count;
  }
  iop_gpr[rt]=loaded;iop_lw_value=loaded;++iop_lw_reads;iop_lw_reject=0;""")
patch(c,'fprintf(f,"BUILD 151 IOP LW FAULT:', '''fprintf(f,"BUILD 152 IOP LW PROVENANCE: COUNT=%u (last 32 successful LW; destination write is immediate, R3000 load-delay not yet modeled)\\n",iop_lw152_count);
 for(unsigned j=0;j<iop_lw152_count;++j){
  const unsigned k=(iop_lw152_head+32u-iop_lw152_count+j)&31u;
  fprintf(f,"IOP152 LW %02u PC=%08X VA=%08X RT=%u VALUE=%08X\\n",j,
   iop_lw152_pc[k],iop_lw152_va[k],iop_lw152_rt[k],iop_lw152_val[k]);
 }
 fprintf(f,"BUILD 151 IOP LW FAULT:''')
print("Build152: IOP LW provenance ring installed (no guest semantics changed)")
