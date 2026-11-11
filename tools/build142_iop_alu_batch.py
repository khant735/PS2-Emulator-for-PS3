#!/usr/bin/env python3
"""Build 142: batch IOP MIPS-I integer ALU, shifts and HI/LO operations.
Existing decoder/MMIO/trace patches remain intact. Overflow exceptions,
load delay and interrupt fidelity remain separate work.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
c=root/"source/emu_core.cpp"
h=root/"include/emu_core.h"
def once(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build142 anchor mismatch {path.name}: count={s.count(old)} {old[:90]!r}")
 path.write_text(s.replace(old,new,1))
once(h,"uint64_t iop_sltu_count;","uint64_t iop_batch142_ops;uint32_t iop_batch142_last_pc,iop_batch142_last_ins;\n uint64_t iop_sltu_count;")
once(c,"iop_sltu_count=0;","iop_batch142_ops=0;iop_batch142_last_pc=iop_batch142_last_ins=0;\n iop_sltu_count=0;")
needle='else {snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP unsupported PC=%08X OP=%08X",addr,ins);'
batch='''else if(op==0 && (
    fn==0||fn==2||fn==3||fn==4||fn==6||fn==7||
    fn==16||fn==17||fn==18||fn==19||fn==24||fn==25||
    fn==26||fn==27||fn==32||fn==34||fn==35||
    fn==36||fn==38||fn==39||fn==42)){
  const uint32_t a=iop_gpr[rs],b=iop_gpr[rt],sa=(ins>>6)&31u;
  const uint32_t shift=b&31u;
  switch(fn){
   case 0:iop_gpr[rd]=b<<sa;break; // SLL
   case 2:iop_gpr[rd]=b>>sa;break; // SRL
   case 3:iop_gpr[rd]=(uint32_t)((int32_t)b>>sa);break; // SRA
   case 4:iop_gpr[rd]=b<<(a&31u);break; // SLLV
   case 6:iop_gpr[rd]=b>>(a&31u);break; // SRLV
   case 7:iop_gpr[rd]=(uint32_t)((int32_t)b>>(a&31u));break; // SRAV
   case 16:iop_gpr[rd]=iop_hi;break; // MFHI
   case 17:iop_hi=a;break; // MTHI
   case 18:iop_gpr[rd]=iop_lo;break; // MFLO
   case 19:iop_lo=a;break; // MTLO
   case 24:{int64_t v=(int64_t)(int32_t)a*(int64_t)(int32_t)b;
     iop_lo=(uint32_t)v;iop_hi=(uint32_t)((uint64_t)v>>32);break;} // MULT
   case 25:{uint64_t v=(uint64_t)a*(uint64_t)b;
     iop_lo=(uint32_t)v;iop_hi=(uint32_t)(v>>32);break;} // MULTU
   case 26:if(b!=0){ // DIV signed, avoid INT_MIN/-1 UB
     if(a==0x80000000u&&b==0xffffffffu){iop_lo=0x80000000u;iop_hi=0;}
     else{iop_lo=(uint32_t)((int32_t)a/(int32_t)b);
          iop_hi=(uint32_t)((int32_t)a%(int32_t)b);}
    }break;
   case 27:if(b!=0){iop_lo=a/b;iop_hi=a%b;}break; // DIVU
   case 32: // ADD: overflow trapping still pending
   case 33:iop_gpr[rd]=a+b;break;
   case 34: // SUB: overflow trapping still pending
   case 35:iop_gpr[rd]=a-b;break;
   case 36:iop_gpr[rd]=a&b;break;
   case 38:iop_gpr[rd]=a^b;break;
   case 39:iop_gpr[rd]=~(a|b);break;
   case 42:iop_gpr[rd]=((int32_t)a<(int32_t)b)?1u:0u;break;
  }
  ++iop_batch142_ops;iop_batch142_last_pc=addr;iop_batch142_last_ins=ins;
 }
 else if(op==11){ // SLTIU sign-extends immediate before unsigned comparison
  iop_gpr[rt]=(iop_gpr[rs]<(uint32_t)imm)?1u:0u;
  ++iop_batch142_ops;iop_batch142_last_pc=addr;iop_batch142_last_ins=ins;
 }
 else if(op==14){iop_gpr[rt]=iop_gpr[rs]^(ins&65535u);
  ++iop_batch142_ops;iop_batch142_last_pc=addr;iop_batch142_last_ins=ins;
 }
 '''
once(c,needle,batch+needle)
once(c,'fprintf(f,"BUILD 141 IOP SLTU:', '''fprintf(f,"BUILD 142 IOP ALU BATCH: EXECUTED=%llu LAST_PC=%08X LAST_INSN=%08X (MIPS-I ALU/shifts/HI-LO; overflow and load-delay fidelity pending)\\n",
 (unsigned long long)iop_batch142_ops,iop_batch142_last_pc,iop_batch142_last_ins);
 fprintf(f,"BUILD 141 IOP SLTU:''')
print("Build142: integer ALU/shift/HI-LO batch installed")
