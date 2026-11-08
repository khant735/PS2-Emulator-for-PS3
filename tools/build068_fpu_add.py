#!/usr/bin/env python3
"""Build 068: EE COP1 ADD.S and ADDA.S initial arithmetic support."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 068 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t cp0[32],fpr[32];","uint32_t cp0[32],fpr[32];uint32_t fpu_acc,fpu_last_opcode,fpu_last_result;uint64_t fpu_adds,fpu_addas;")
p=root/"source/emu_core.cpp"
change(p,"memset(fpr,0,sizeof(fpr));","memset(fpr,0,sizeof(fpr));fpu_acc=fpu_last_opcode=fpu_last_result=0;fpu_adds=fpu_addas=0;")
change(p,'if((rs!=0&&rs!=4)||(opcode&0x7ff))return halt(UNSUPPORTED,"COP1 operation not implemented (MFC1/MTC1 only)");\n  if(rs==0){dest=rt;result=sx32(fpr[rd]);write=true;}\n  else fpr[rd]=uint32_t(b);', '''if(rs==16 && ((opcode&63u)==0u || (opcode&63u)==24u)){
   // COP1.S: fs bits 15..11, ft bits 20..16, fd bits 10..6.
   // 0x18 is ADDA.S (accumulator), NOT ADD.S (0x00).
   unsigned fs=(opcode>>11)&31u,ft=(opcode>>16)&31u,fd=(opcode>>6)&31u;
   float x,y,z;
   uint32_t xb=fpr[fs],yb=fpr[ft],zb;
   memcpy(&x,&xb,4);memcpy(&y,&yb,4);
   z=x+y;memcpy(&zb,&z,4);
   if((opcode&63u)==24u){fpu_acc=zb;++fpu_addas;}
   else{fpr[fd]=zb;++fpu_adds;}
   fpu_last_opcode=opcode;fpu_last_result=zb;
  }else{
   if((rs!=0&&rs!=4)||(opcode&0x7ff))return halt(UNSUPPORTED,"COP1 operation not implemented (MFC1/MTC1 and ADD.S/ADDA.S only)");
   if(rs==0){dest=rt;result=sx32(fpr[rd]);write=true;}
   else fpr[rd]=uint32_t(b);
  }''')
change(p,'for(unsigned i=0;i<32;i++)fprintf(f,"F%02u=%08X\\n",i,fpr[i]);', 'fprintf(f,"FPU ADD.S=%llu ADDA.S=%llu ACC=%08X LAST_OPCODE=%08X LAST_RESULT=%08X (host float approximation; EE rounding/flags unimplemented)\\n",(unsigned long long)fpu_adds,(unsigned long long)fpu_addas,fpu_acc,fpu_last_opcode,fpu_last_result);\n for(unsigned i=0;i<32;i++)fprintf(f,"F%02u=%08X\\n",i,fpr[i]);')
change(root/"source/emu_ui.inc","BUILD 067 - IPU INPUT FIFO","BUILD 068 - FPU ADD/ADDA")
print("Build 068 FPU ADD.S and ADDA.S applied")
