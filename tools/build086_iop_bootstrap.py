#!/usr/bin/env python3
"""Build 086: independent, bounded IOP R3000 bootstrap interpreter (diagnostic)."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build086 anchor {p.name}: {a[:80]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_probe_reads;","""uint64_t iop_probe_reads;
 // IOP diagnostic CPU: separate R3000 state, no SIF/IRQ/DMA emulation.
 uint32_t iop_pc,iop_next,iop_gpr[32],iop_hi,iop_lo,iop_last_opcode;
 uint64_t iop_instructions;bool iop_running,iop_delay;
 char iop_stop_reason[96];
 bool iopStep();""")
patch(c,"void Core::reset(uint32_t entry){","""void Core::reset(uint32_t entry){""")
patch(c,"hi=lo=0;pc=entry;","""memset(iop_gpr,0,sizeof(iop_gpr));iop_pc=0xbfc00000u;iop_next=iop_pc+4;
 iop_hi=iop_lo=iop_last_opcode=0;iop_instructions=0;iop_running=(entry==0xbfc00000u);
 iop_delay=false;iop_stop_reason[0]=0;
 hi=lo=0;pc=entry;""")
patch(c,"bool Core::step(){","""bool Core::iopStep(){
 if(!iop_running)return false;
 uint32_t addr=iop_pc,physaddr=addr;
 if(addr>=0x80000000u&&addr<0xc0000000u)physaddr=addr&0x1fffffffu;
 const unsigned char*ptr=NULL;
 if(physaddr<IOP_RAM&&physaddr+4<=IOP_RAM)ptr=iop_ram+physaddr;
 else if(physaddr>=0x1fc00000u&&physaddr<0x20000000u&&physaddr-0x1fc00000u+4<=ROM)
  ptr=rom+(physaddr-0x1fc00000u);
 if(!ptr||(addr&3)){snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP unmapped fetch %08X",addr);iop_running=false;return false;}
 uint32_t ins=le32(ptr);iop_last_opcode=ins;
 unsigned op=ins>>26,rs=(ins>>21)&31,rt=(ins>>16)&31,rd=(ins>>11)&31,fn=ins&63;
 uint32_t old_next=iop_next,new_next=old_next+4;
 int32_t imm=(int16_t)(ins&65535);bool branch=false;
 if(ins==0){} // NOP
 else if(op==15)iop_gpr[rt]=ins<<16;
 else if(op==13)iop_gpr[rt]=iop_gpr[rs]|(ins&65535);
 else if(op==12)iop_gpr[rt]=iop_gpr[rs]&(ins&65535);
 else if(op==9)iop_gpr[rt]=iop_gpr[rs]+(uint32_t)imm;
 else if(op==4||op==5){branch=true;if((iop_gpr[rs]==iop_gpr[rt])==(op==4))new_next=old_next+(uint32_t)(imm*4);}
 else if(op==2||op==3){branch=true;new_next=(old_next&0xf0000000u)|((ins&0x03ffffffu)<<2);if(op==3)iop_gpr[31]=old_next+4;}
 else if(op==0&&fn==8){branch=true;new_next=iop_gpr[rs];}
 else if(op==0&&fn==33)iop_gpr[rd]=iop_gpr[rs]+iop_gpr[rt];
 else if(op==0&&fn==37)iop_gpr[rd]=iop_gpr[rs]|iop_gpr[rt];
 else {snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP unsupported PC=%08X OP=%08X",addr,ins);iop_running=false;return false;}
 if(branch&&iop_delay){snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP branch in delay slot PC=%08X",addr);iop_running=false;return false;}
 iop_pc=old_next;iop_next=new_next;iop_delay=branch;iop_gpr[0]=0;++iop_instructions;
 return true;
}
bool Core::step(){""")
patch(c,"if(stop!=NONE)return false;","""if(stop!=NONE)return false;
 // Diagnostic only: one IOP instruction per eight EE instructions, no fabricated SIF response.
 if((instructions&7u)==0&&iop_running)iopStep();""")
patch(c,'fprintf(f,"IOP RAM: 2 MiB, 8 MiB mirrored EE window; IOP CPU not running\\n', '''fprintf(f,"BUILD 086 IOP BOOTSTRAP: PC=%08X NEXT=%08X OPCODE=%08X RETIRED=%llu RUNNING=%u REASON=%s (minimal R3000 diagnostic, no SIF/DMA/IRQ)\\n",
 iop_pc,iop_next,iop_last_opcode,(unsigned long long)iop_instructions,iop_running?1u:0u,iop_stop_reason[0]?iop_stop_reason:"none");
 fprintf(f,"IOP RAM: 2 MiB, 8 MiB mirrored EE window; IOP CPU diagnostic active\\n''')
patch(u,"BUILD 085 - SIF POLL DIAGNOSTICS","BUILD 086 - IOP BOOTSTRAP")
print("Build 086 IOP bootstrap applied")
