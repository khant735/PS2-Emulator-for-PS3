#!/usr/bin/env python3
"""Build 074: little-endian MIPS64 LDL, unaligned left-merge load."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 074 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t iop_debug3800_reads;","uint64_t ee_ldl_count;uint32_t ee_ldl_last_pc,ee_ldl_last_addr;uint64_t iop_debug3800_reads;")
p=root/"source/emu_core.cpp"
change(p,"iop_debug3800_reads=0;iop_debug3800_last_pc=0;","iop_debug3800_reads=0;iop_debug3800_last_pc=0;ee_ldl_count=0;ee_ldl_last_pc=ee_ldl_last_addr=0;")
change(p," }else if(op==32||op==33||op==35||op==36||op==37||op==39||op==55){",''' }else if(op==26){
  // EE LDL (little-endian): merge bytes from aligned doubleword
  // [offset..7] into the most significant destination bytes.
  // Keep the low (7-offset) bytes of the original rt unchanged.
  // Read all 8 bytes through the normal mapped-memory/MMIO interface.
  uint32_t aligned=addr&~7u;
  unsigned offset=addr&7u;
  unsigned char*ptr=address(aligned,8,false);
  uint64_t word=0;
  if(ptr){for(unsigned i=0;i<8;i++)word|=uint64_t(ptr[i])<<(8*i);}
  else if(!mmioRead(aligned,8,word))return memoryHalt(aligned,8,false,false);
  unsigned shift=8u*(7u-offset);
  uint64_t keep=shift?((uint64_t(1)<<shift)-1u):0u;
  result=(b&keep)|(word<<shift);
  write=true;dest=rt;
  ++ee_ldl_count;ee_ldl_last_pc=pc;ee_ldl_last_addr=addr;
 }else if(op==32||op==33||op==35||op==36||op==37||op==39||op==55){''')
change(p,'fprintf(f,"IOP DEBUG 1F803800 EXPERIMENTAL HALFWORD ZERO:', 'fprintf(f,"EE LDL little-endian merge: COUNT=%llu LAST_PC=%08X LAST_ADDR=%08X\\n",(unsigned long long)ee_ldl_count,ee_ldl_last_pc,ee_ldl_last_addr);\n fprintf(f,"IOP DEBUG 1F803800 EXPERIMENTAL HALFWORD ZERO:')
change(p,'(pc==0x8000EF60u && opcode==0x944A0000u)?"observed unsupported MMIO (no synthesized value)":"not at known probe"', '(iop_debug3800_reads?"previously observed; experimental zero response":"not observed")')
change(root/"source/emu_ui.inc","BUILD 073 - IOP 3800 PROBE","BUILD 074 - EE LDL")
print("Build 074 EE LDL applied")
