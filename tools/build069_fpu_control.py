#!/usr/bin/env python3
"""Build 069: COP1 CFC1/CTC1 control-register transfers (initial FCR model)."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 069 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t fpu_acc,fpu_last_opcode,fpu_last_result;","uint32_t fpu_control[32];uint64_t fpu_cfc1_reads,fpu_ctc1_writes;uint32_t fpu_last_control_index,fpu_last_control_value;uint32_t fpu_acc,fpu_last_opcode,fpu_last_result;")
p=root/"source/emu_core.cpp"
change(p,"fpu_acc=fpu_last_opcode=fpu_last_result=0;fpu_adds=fpu_addas=0;","fpu_acc=fpu_last_opcode=fpu_last_result=0;fpu_adds=fpu_addas=0;memset(fpu_control,0,sizeof(fpu_control));fpu_control[0]=0x00002E00u;fpu_cfc1_reads=fpu_ctc1_writes=0;fpu_last_control_index=fpu_last_control_value=0;")
change(p,'if((rs!=0&&rs!=4)||(opcode&0x7ff))return halt(UNSUPPORTED,"COP1 operation not implemented (MFC1/MTC1 and ADD.S/ADDA.S only)");\n   if(rs==0){dest=rt;result=sx32(fpr[rd]);write=true;}\n   else fpr[rd]=uint32_t(b);', '''if((opcode&0x7ffu)!=0u || (rs!=0 && rs!=2 && rs!=4 && rs!=6))
    return halt(UNSUPPORTED,"COP1 operation not implemented (FPU data/control transfers and ADD.S/ADDA.S only)");
   if(rs==0){dest=rt;result=sx32(fpr[rd]);write=true;}
   else if(rs==4){fpr[rd]=uint32_t(b);}
   else if(rs==2){
    // CFC1: control-register read, sign-extended into EE GPR.
    dest=rt;result=sx32(fpu_control[rd]);write=true;
    ++fpu_cfc1_reads;fpu_last_control_index=rd;fpu_last_control_value=fpu_control[rd];
   }else{
    // CTC1: FCR0 is read-only. Other registers use diagnostic storage.
    // FCR31 exception/rounding side effects are not modeled yet.
    if(rd!=0)fpu_control[rd]=uint32_t(b);
    ++fpu_ctc1_writes;fpu_last_control_index=rd;fpu_last_control_value=fpu_control[rd];
   }''')
change(p,'fprintf(f,"FPU ADD.S=', 'fprintf(f,"FPU COP1 control (initial storage; FCR31 side effects unimplemented): CFC1=%llu CTC1=%llu FCR0=%08X FCR31=%08X LAST_INDEX=%u LAST_VALUE=%08X\\n",(unsigned long long)fpu_cfc1_reads,(unsigned long long)fpu_ctc1_writes,fpu_control[0],fpu_control[31],fpu_last_control_index,fpu_last_control_value);\n fprintf(f,"FPU ADD.S=')
change(root/"source/emu_ui.inc","BUILD 068 - FPU ADD/ADDA","BUILD 069 - FPU CONTROL")
print("Build 069 COP1 CFC1/CTC1 applied")
