#!/usr/bin/env python3
"""Build 157: bounded pre-execution IOP fault window; diagnostic only."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
c=r/"source/emu_core.cpp"
s=c.read_text()
anchor='fprintf(f,"BUILD 153 IOP POINTER PROVENANCE:'
assert s.count(anchor)==1, "Build157 trace anchor mismatch"
addition=r'''fprintf(f,"BUILD 157 IOP FAULT WINDOW: last 128 attempted IOP instructions, pre-execution registers; diagnostic only\n");
 if(iop_fault151_seen){
  const unsigned n157=iop_history_count<128u?iop_history_count:128u;
  for(unsigned j157=0;j157<n157;++j157){
   const unsigned k157=(iop_history_head+4096u-n157+j157)&4095u;
   const IopTrace &t157=iop_history[k157];
   const unsigned rs157=(t157.opcode>>21)&31u,rt157=(t157.opcode>>16)&31u;
   const int32_t imm157=(int16_t)(t157.opcode&65535u);
   const uint32_t *g157=iop153_pre_gpr[k157];
   const uint32_t ea157=(rs157==6u)?(g157[4]+(uint32_t)imm157):0u;
   fprintf(f,"IOP157 %03u PC=%08X OP=%08X RS=%u RT=%u V0=%08X V1=%08X A0=%08X A1=%08X A2=%08X T0=%08X T1=%08X RA=%08X A2_EA=%08X\n",
    j157,t157.pc,t157.opcode,rs157,rt157,g157[0],g157[1],g157[2],g157[3],g157[4],g157[5],g157[6],g157[7],ea157);
  }
 }
 '''
s=s.replace(anchor,addition+anchor,1)
identity="BUILD_NUMBER=154\\nBUILD_VERSION=dev-build.154"
assert s.count(identity)==1, "Build157 identity anchor mismatch"
s=s.replace(identity,"BUILD_NUMBER=157\\nBUILD_VERSION=dev-build.157",1)
c.write_text(s)
print("Build157 diagnostic installed")
