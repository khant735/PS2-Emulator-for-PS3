#!/usr/bin/env python3
"""Build 094: writable IOP 0x1F801010 register and bounded instruction history."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build094 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_dma_madr_reads;uint32_t iop_dma_madr_value;","""uint64_t iop_dma_madr_reads;uint32_t iop_dma_madr_value;
 uint64_t iop_memctrl_writes;
 uint32_t iop_memctrl_last_pc,iop_memctrl_last_value;
 struct IopTrace {uint32_t pc,opcode;};
 IopTrace iop_history[4096];uint32_t iop_history_head,iop_history_count;""")
patch(c,"iop_dma_madr_reads=0;iop_dma_madr_value=0;","""iop_dma_madr_reads=0;iop_dma_madr_value=0;
 iop_memctrl_writes=0;iop_memctrl_last_pc=iop_memctrl_last_value=0;
 iop_history_head=iop_history_count=0;""")
patch(c,"uint32_t ins=le32(ptr);iop_last_opcode=ins;","""uint32_t ins=le32(ptr);iop_last_opcode=ins;
 iop_history[iop_history_head].pc=addr;
 iop_history[iop_history_head].opcode=ins;
 iop_history_head=(iop_history_head+1u)&4095u;
 if(iop_history_count<4096u)++iop_history_count;""")
patch(c,"if(pa>IOP_RAM||IOP_RAM-pa<4u){","""if(pa==0x1f801010u){
   iop_dma_madr_value=iop_gpr[rt]; // historical variable name; now memory-control latch
   iop_memctrl_last_pc=addr;iop_memctrl_last_value=iop_gpr[rt];
   ++iop_memctrl_writes;
  }else if(pa>IOP_RAM||IOP_RAM-pa<4u){""")
patch(c,"  uint32_t value=iop_gpr[rt];\n  iop_ram[pa]","  uint32_t value=iop_gpr[rt];\n  if(pa!=0x1f801010u){iop_ram[pa]")
patch(c,"  iop_ram[pa+3]=(unsigned char)(value>>24);","  iop_ram[pa+3]=(unsigned char)(value>>24);}")
patch(c,'fprintf(f,"BUILD 093 IOP MEMORY CONTROL 1010:', '''fprintf(f,"BUILD 094 IOP MEMORY CONTROL: WRITES=%llu LAST_PC=%08X LAST_VALUE=%08X READS=%llu CURRENT=%08X (timing effects not modeled)\\n",
 (unsigned long long)iop_memctrl_writes,iop_memctrl_last_pc,iop_memctrl_last_value,
 (unsigned long long)iop_dma_madr_reads,iop_dma_madr_value);
 fprintf(f,"BUILD 094 IOP INSTRUCTION HISTORY: COUNT=%u (last 4096 attempts, oldest first)\\n",iop_history_count);
 for(uint32_t k=0;k<iop_history_count;++k){
  const IopTrace &t=iop_history[(iop_history_head+4096u-iop_history_count+k)&4095u];
  fprintf(f,"IOP TRACE %04u PC=%08X OPCODE=%08X\\n",k,t.pc,t.opcode);
 }
 fprintf(f,"BUILD 093 IOP MEMORY CONTROL 1010:''')
patch(u,"BUILD 093 - IOP ADDI","BUILD 094 - IOP MEMORY CONTROL")
print("Build 094 IOP memory-control and instruction history applied")
