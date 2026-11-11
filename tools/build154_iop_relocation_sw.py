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
# The handler has been augmented by many earlier patches. Instead of matching
# its changing write syntax, attach a pre-execution diagnostic at the single
# stable instruction-history site, guarded by opcode and PC.
patch(c,"iop_history[iop_history_head].pc=addr;", """if(addr==0x00000ec8u && ((ins>>26)&63u)==43u){
  const unsigned rs154=(ins>>21)&31u,rt154=(ins>>16)&31u;
  const int32_t off154=(int16_t)(ins&65535u);
  const uint32_t va154=iop_gpr[rs154]+(uint32_t)off154;
  const uint32_t pa154=(va154>=0x80000000u&&va154<0xc0000000u)?(va154&0x1fffffffu):va154;
  const unsigned k154=iop154_head&63u;
  const bool mapped154=((va154&3u)==0 && pa154<=IOP_RAM && IOP_RAM-pa154>=4u);
  iop154_pc[k154]=addr;iop154_va[k154]=va154;iop154_pa[k154]=pa154;
  iop154_rs[k154]=rs154;iop154_rt[k154]=rt154;
  iop154_base[k154]=iop_gpr[rs154];iop154_src[k154]=iop_gpr[rt154];
  iop154_value[k154]=iop_gpr[rt154];
  iop154_v0[k154]=iop_gpr[2];iop154_v1[k154]=iop_gpr[3];
  iop154_t0[k154]=iop_gpr[8];iop154_t1[k154]=iop_gpr[9];
  iop154_before[k154]=mapped154?le32(iop_ram+pa154):0xffffffffu;
  // This records the word the existing SW implementation is expected to write,
  // without adding or modifying a store or assuming success on a bad address.
  iop154_after[k154]=mapped154?iop_gpr[rt154]:0xffffffffu;
  iop154_head=(iop154_head+1u)&63u;
  if(iop154_count<64u)++iop154_count;
 }
 iop_history[iop_history_head].pc=addr;""")
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
