#!/usr/bin/env python3
"""Build 153: pre-execution IOP pointer/register provenance, without changing guest semantics."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build153 anchor mismatch {path.name}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_jalr_count;","""uint32_t iop153_pre_gpr[4096][8];
 uint64_t iop_jalr_count;""")
patch(c,"iop_history[iop_history_head].pc=addr;","""// Capture register state BEFORE instruction execution, aligned with Build094 history.
 // IOP is MIPS R3000: 32-bit addresses and 32-bit GPRs (not host pointer width).
 // Slots: v0,v1,a0,a1,a2,t0,t1,ra.
 {const unsigned k=iop_history_head;
  const unsigned regs[8]={2,3,4,5,6,8,9,31};
  for(unsigned j=0;j<8;++j)iop153_pre_gpr[k][j]=iop_gpr[regs[j]];
 }
 iop_history[iop_history_head].pc=addr;""")
patch(c,'fprintf(f,"BUILD 152 IOP LW PROVENANCE:', '''fprintf(f,"BUILD 153 IOP POINTER PROVENANCE: IOP_GPR_BITS=32 IOP_ADDRESS_BITS=32 HOST_POINTER_SIZE=%u (host size is diagnostic only; guest pointers must not use it)\\n",(unsigned)sizeof(void*));
 if(iop_fault151_seen){
  const unsigned n=iop_history_count<48u?iop_history_count:48u;
  fprintf(f,"IOP153 PRE-EXECUTION HISTORY: COUNT=%u REGISTERS=V0,V1,A0,A1,A2,T0,T1,RA\\n",n);
  for(unsigned j=0;j<n;++j){
   const unsigned k=(iop_history_head+4096u-n+j)&4095u;
   const IopTrace &t=iop_history[k];
   fprintf(f,"IOP153 %02u PC=%08X OP=%08X V0=%08X V1=%08X A0=%08X A1=%08X A2=%08X T0=%08X T1=%08X RA=%08X\\n",j,t.pc,t.opcode,
    iop153_pre_gpr[k][0],iop153_pre_gpr[k][1],iop153_pre_gpr[k][2],iop153_pre_gpr[k][3],
    iop153_pre_gpr[k][4],iop153_pre_gpr[k][5],iop153_pre_gpr[k][6],iop153_pre_gpr[k][7]);
  }
 }
 fprintf(f,"BUILD 152 IOP LW PROVENANCE:''')
# Fix the older Build150 embedded identity, which otherwise misleadingly labels later builds.
patch(c,"BUILD_NUMBER=150\\nBUILD_VERSION=dev-build.150","BUILD_NUMBER=153\\nBUILD_VERSION=dev-build.153")
print("Build153: IOP pointer-size and pre-execution register provenance installed")
