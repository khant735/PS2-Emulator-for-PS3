#!/usr/bin/env python3
"""Build 076: little-endian MIPS64 SDL/SDR with byte-preserving memory merges."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 076 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t ee_ldr_count;","uint64_t ee_sdl_count,ee_sdr_count;uint32_t ee_store_last_pc,ee_store_last_addr;uint64_t ee_ldr_count;")
p=root/"source/emu_core.cpp"
change(p,"ee_ldr_count=0;ee_ldr_last_pc=ee_ldr_last_addr=0;","ee_ldr_count=0;ee_ldr_last_pc=ee_ldr_last_addr=0;ee_sdl_count=ee_sdr_count=0;ee_store_last_pc=ee_store_last_addr=0;")
change(p," }else if(op==27){",''' }else if(op==44||op==45){
  // SDL (44) / SDR (45), little-endian byte-preserving unaligned stores.
  // Read/modify/write the aligned 64-bit word, preserving all other bytes.
  const uint32_t aligned=addr&~7u;
  const unsigned offset=addr&7u;
  unsigned char*ptr=address(aligned,8,true);
  uint64_t old=0;
  if(ptr){for(unsigned i=0;i<8;i++)old|=uint64_t(ptr[i])<<(8*i);}
  else if(!mmioRead(aligned,8,old))return memoryHalt(aligned,8,true,false);
  uint64_t merged=old;
  for(unsigned i=0;i<8;i++){
   if(op==44 ? i<=offset : i>=offset){
    // SDL takes high register bytes; SDR takes low register bytes.
    const unsigned sourceByte=op==44 ? i+7u-offset : i-offset;
    const uint64_t mask=uint64_t(255)<<(8*i);
    merged=(merged&~mask)|(((b>>(8*sourceByte))&255u)<<(8*i));
   }
  }
  if(ptr){for(unsigned i=0;i<8;i++)ptr[i]=(unsigned char)(merged>>(8*i));}
  else if(!mmioWrite(aligned,8,merged))return memoryHalt(aligned,8,true,false);
  if(op==44)++ee_sdl_count;else ++ee_sdr_count;
  ee_store_last_pc=pc;ee_store_last_addr=addr;
 }else if(op==27){''')
change(p,'fprintf(f,"EE LDR little-endian merge:', 'fprintf(f,"EE SDL/SDR little-endian stores: SDL=%llu SDR=%llu LAST_PC=%08X LAST_ADDR=%08X\\n",(unsigned long long)ee_sdl_count,(unsigned long long)ee_sdr_count,ee_store_last_pc,ee_store_last_addr);\n fprintf(f,"EE LDR little-endian merge:')
change(root/"source/emu_ui.inc","BUILD 075 - EE LDL/LDR","BUILD 076 - EE SDL/SDR")
print("Build 076 EE SDL/SDR applied")
