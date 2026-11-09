#!/usr/bin/env python3
"""Build 121: bounded IOP instruction history for BIOS trace diagnosis.
Keeps last 64 attempted IOP instructions, including the failing opcode.
No save-state changes.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit("Build121 anchor mismatch "+str(p)+" "+repr(a))
 p.write_text(s.replace(a,b,1))
patch(h,"uint32_t iop_pc,iop_next,iop_gpr[32],iop_cop0[32],iop_hi,iop_lo,iop_last_opcode;",
"""struct IopTraceEntry { uint32_t pc,opcode; };
 enum { IOP_TRACE_CAPACITY=64 };
 IopTraceEntry iop_trace[IOP_TRACE_CAPACITY];
 uint32_t iop_trace_head,iop_trace_count;
 uint32_t iop_pc,iop_next,iop_gpr[32],iop_cop0[32],iop_hi,iop_lo,iop_last_opcode;""")
patch(c,"iop_hi=iop_lo=iop_last_opcode=0;iop_instructions=0;",
"""iop_hi=iop_lo=iop_last_opcode=0;iop_instructions=0;
 iop_trace_head=iop_trace_count=0;memset(iop_trace,0,sizeof(iop_trace));""")
patch(c,"uint32_t ins=le32(ptr);iop_last_opcode=ins;",
"""uint32_t ins=le32(ptr);iop_last_opcode=ins;
 iop_trace[iop_trace_head].pc=addr;
 iop_trace[iop_trace_head].opcode=ins;
 iop_trace_head=(iop_trace_head+1)%IOP_TRACE_CAPACITY;
 if(iop_trace_count<IOP_TRACE_CAPACITY)++iop_trace_count;""")
patch(c,'fprintf(f,"BUILD 086 IOP BOOTSTRAP:', '''fprintf(f,"BUILD 121 IOP RECENT INSTRUCTION ATTEMPTS: COUNT=%u (oldest first)\\n",iop_trace_count);
 for(uint32_t j=0;j<iop_trace_count;++j){
  const IopTraceEntry &e=iop_trace[(iop_trace_head+IOP_TRACE_CAPACITY-iop_trace_count+j)%IOP_TRACE_CAPACITY];
  fprintf(f,"IOP TRACE %02u PC=%08X OP=%08X\\n",j,e.pc,e.opcode);
 }
 fprintf(f,"BUILD 086 IOP BOOTSTRAP:''')
print("Build 121 IOP instruction history diagnostics installed")
