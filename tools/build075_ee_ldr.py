#!/usr/bin/env python3
"""Build 075: EE little-endian LDR, paired with Build 074 LDL."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 075 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t ee_ldl_count;","uint64_t ee_ldr_count;uint32_t ee_ldr_last_pc,ee_ldr_last_addr;uint64_t ee_ldl_count;")
p=root/"source/emu_core.cpp"
change(p,"ee_ldl_count=0;ee_ldl_last_pc=ee_ldl_last_addr=0;","ee_ldl_count=0;ee_ldl_last_pc=ee_ldl_last_addr=0;ee_ldr_count=0;ee_ldr_last_pc=ee_ldr_last_addr=0;")
change(p," }else if(op==26){",''' }else if(op==27){
  // EE LDR little-endian: low (8-offset) bytes come from aligned memory;
  // retain the high offset bytes from the existing destination register.
  uint32_t aligned=addr&~7u;
  unsigned offset=addr&7u;
  unsigned char*ptr=address(aligned,8,false);
  uint64_t word=0;
  if(ptr){for(unsigned i=0;i<8;i++)word|=uint64_t(ptr[i])<<(8*i);}
  else if(!mmioRead(aligned,8,word))return memoryHalt(aligned,8,false,false);
  unsigned shift=8u*offset;
  uint64_t keep=shift?~((uint64_t(1)<<(64u-shift))-1u):0u;
  result=(b&keep)|(word>>shift);
  write=true;dest=rt;
  ++ee_ldr_count;ee_ldr_last_pc=pc;ee_ldr_last_addr=addr;
 }else if(op==26){''')
change(p,'fprintf(f,"EE LDL little-endian merge:', 'fprintf(f,"EE LDR little-endian merge: COUNT=%llu LAST_PC=%08X LAST_ADDR=%08X\\n",(unsigned long long)ee_ldr_count,ee_ldr_last_pc,ee_ldr_last_addr);\n fprintf(f,"EE LDL little-endian merge:')
change(root/"source/emu_ui.inc","BUILD 074 - EE LDL","BUILD 075 - EE LDL/LDR")
print("Build 075 EE LDR applied")
