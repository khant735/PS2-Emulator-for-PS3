#!/usr/bin/env python3
"""Build 151: read-only IOP LW alignment-fault forensic snapshot."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build151 anchor mismatch {p.name}: {a[:90]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_jalr_count;", """uint32_t iop_fault151_pc,iop_fault151_ins,iop_fault151_va,iop_fault151_rs,iop_fault151_rt,iop_fault151_base,iop_fault151_prev_pc,iop_fault151_prev_ins;
 uint32_t iop_fault151_gpr[32];uint32_t iop_fault151_history_pc[16],iop_fault151_history_ins[16];
 uint32_t iop_fault151_history_count;uint32_t iop_fault151_ram[24];uint32_t iop_fault151_seen;
 uint64_t iop_jalr_count;""")
patch(c,"iop_jalr_count=0;", """iop_fault151_pc=iop_fault151_ins=iop_fault151_va=iop_fault151_rs=iop_fault151_rt=iop_fault151_base=iop_fault151_prev_pc=iop_fault151_prev_ins=0;
 iop_fault151_history_count=iop_fault151_seen=0;
 memset(iop_fault151_gpr,0,sizeof(iop_fault151_gpr));
 memset(iop_fault151_history_pc,0,sizeof(iop_fault151_history_pc));
 memset(iop_fault151_history_ins,0,sizeof(iop_fault151_history_ins));
 memset(iop_fault151_ram,0,sizeof(iop_fault151_ram));
 iop_jalr_count=0;""")
patch(c,'if(va&3u){iop_lw_reject=1;', '''if(va&3u){
   iop_fault151_seen=1;iop_fault151_pc=addr;iop_fault151_ins=ins;
   iop_fault151_va=va;iop_fault151_rs=rs;iop_fault151_rt=rt;
   iop_fault151_base=iop_gpr[rs];
   for(unsigned j=0;j<32;++j)iop_fault151_gpr[j]=iop_gpr[j];
   iop_fault151_history_count=iop_history_count<16u?iop_history_count:16u;
   for(unsigned j=0;j<iop_fault151_history_count;++j){
    const IopTrace &t=iop_history[(iop_history_head+4096u-iop_fault151_history_count+j)&4095u];
    iop_fault151_history_pc[j]=t.pc;iop_fault151_history_ins[j]=t.opcode;
   }
   if(iop_fault151_history_count>1){
    iop_fault151_prev_pc=iop_fault151_history_pc[iop_fault151_history_count-2];
    iop_fault151_prev_ins=iop_fault151_history_ins[iop_fault151_history_count-2];
   }
   for(unsigned j=0;j<24;++j){
    const uint32_t pa=0x1df0u+j*4u;
    iop_fault151_ram[j]=le32(iop_ram+pa);
   }
   iop_lw_reject=1;''')
patch(c,'fprintf(f,"BUILD 149 IOP ADD:', '''fprintf(f,"BUILD 151 IOP LW FAULT: SEEN=%u PC=%08X INSN=%08X VA=%08X RS=%u RT=%u BASE=%08X PREV_PC=%08X PREV_INSN=%08X (snapshot before alignment rejection; no CPU semantics changed)\\n",
 iop_fault151_seen,iop_fault151_pc,iop_fault151_ins,iop_fault151_va,iop_fault151_rs,iop_fault151_rt,iop_fault151_base,iop_fault151_prev_pc,iop_fault151_prev_ins);
 if(iop_fault151_seen){
  for(unsigned j=0;j<32;++j)fprintf(f,"IOP151 R%02u=%08X\\n",j,iop_fault151_gpr[j]);
  for(unsigned j=0;j<iop_fault151_history_count;++j)fprintf(f,"IOP151 PREV %02u PC=%08X INSN=%08X\\n",j,iop_fault151_history_pc[j],iop_fault151_history_ins[j]);
  for(unsigned j=0;j<24;++j)fprintf(f,"IOP151 RAM %08X=%08X\\n",0x1df0u+j*4u,iop_fault151_ram[j]);
 }
 fprintf(f,"BUILD 149 IOP ADD:''')
print("Build151 read-only LW fault snapshot installed")
