#!/usr/bin/env python3
"""Build 154: bounded IOP relocation SW provenance; diagnostic only."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build154 anchor mismatch {p.name}: {a[:90]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_jalr_count;","""uint32_t iop154_head,iop154_count;
 uint32_t iop154_pc[64],iop154_va[64],iop154_pa[64],iop154_value[64];
 uint32_t iop154_before[64],iop154_after[64],iop154_rs[64],iop154_rt[64];
 uint32_t iop154_base[64],iop154_src[64],iop154_v0[64],iop154_v1[64],iop154_t0[64],iop154_t1[64];
 uint64_t iop_jalr_count;""")
patch(c,"iop_jalr_count=0;","""iop154_head=iop154_count=0;
 memset(iop154_pc,0,sizeof(iop154_pc));
 memset(iop154_va,0,sizeof(iop154_va));
 memset(iop154_pa,0,sizeof(iop154_pa));
 memset(iop154_value,0,sizeof(iop154_value));
 memset(iop154_before,0,sizeof(iop154_before));
 memset(iop154_after,0,sizeof(iop154_after));
 memset(iop154_rs,0,sizeof(iop154_rs));
 memset(iop154_rt,0,sizeof(iop154_rt));
 memset(iop154_base,0,sizeof(iop154_base));
 memset(iop154_src,0,sizeof(iop154_src));
 memset(iop154_v0,0,sizeof(iop154_v0));
 memset(iop154_v1,0,sizeof(iop154_v1));
 memset(iop154_t0,0,sizeof(iop154_t0));
 memset(iop154_t1,0,sizeof(iop154_t1));
 iop_jalr_count=0;""")
# Target only the IOP SW handler's unique code sequence, including the
# Build094 memory-control guard. Other emulated RAM writes must be untouched.
patch(c,"  uint32_t value=iop_gpr[rt];\\n  if(pa!=0x1f801010u){iop_ram[pa]=(unsigned char)value;", """  uint32_t value=iop_gpr[rt];
  // Capture the relocation store before any RAM bytes are overwritten.
  const bool trace154=(addr==0x00000ec8u);
  unsigned slot154=0;
  if(trace154){
   slot154=iop154_head&63u;
   iop154_pc[slot154]=addr;iop154_va[slot154]=va;iop154_pa[slot154]=pa;
   iop154_value[slot154]=value;iop154_before[slot154]=le32(iop_ram+pa);
   iop154_rs[slot154]=rs;iop154_rt[slot154]=rt;
   iop154_base[slot154]=iop_gpr[rs];iop154_src[slot154]=iop_gpr[rt];
   iop154_v0[slot154]=iop_gpr[2];iop154_v1[slot154]=iop_gpr[3];
   iop154_t0[slot154]=iop_gpr[8];iop154_t1[slot154]=iop_gpr[9];
  }
  if(pa!=0x1f801010u){iop_ram[pa]=(unsigned char)value;""")
# After the entire RAM store, record outcome; avoid generic byte-write anchors.
patch(c,"  iop_ram[pa+3]=(unsigned char)(value>>24);}", """  iop_ram[pa+3]=(unsigned char)(value>>24);}
  if(trace154){
   iop154_after[slot154]=le32(iop_ram+pa);
   iop154_head=(iop154_head+1u)&63u;
   if(iop154_count<64u)++iop154_count;
  }""")
patch(c,'fprintf(f,"BUILD 153 IOP POINTER PROVENANCE:', '''fprintf(f,"BUILD 154 IOP RELOCATION SW: COUNT=%u (last 64 writes at PC=00000EC8; RAM only; before/after snapshots)\\n",iop154_count);
 for(unsigned j=0;j<iop154_count;++j){
  const unsigned k=(iop154_head+64u-iop154_count+j)&63u;
  fprintf(f,"IOP154 SW %02u PC=%08X VA=%08X PA=%08X RS=%u RT=%u BASE=%08X SRC=%08X BEFORE=%08X AFTER=%08X V0=%08X V1=%08X T0=%08X T1=%08X\\n",j,
   iop154_pc[k],iop154_va[k],iop154_pa[k],iop154_rs[k],iop154_rt[k],
   iop154_base[k],iop154_src[k],iop154_before[k],iop154_after[k],
   iop154_v0[k],iop154_v1[k],iop154_t0[k],iop154_t1[k]);
 }
 fprintf(f,"BUILD 153 IOP POINTER PROVENANCE:''')
patch(c,"BUILD_NUMBER=153\\nBUILD_VERSION=dev-build.153","BUILD_NUMBER=154\\nBUILD_VERSION=dev-build.154")
print("Build154 relocation SW provenance installed")
