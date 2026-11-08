#!/usr/bin/env python3
"""Regression of little-endian LDL/LDR merge across all 8 alignments."""
MASK=(1<<64)-1
def ldl(old,word,offset):
 shift=8*(7-offset)
 keep=(1<<shift)-1 if shift else 0
 return ((old&keep)|(word<<shift))&MASK
def ldr(old,word,offset):
 shift=8*offset
 keep=(~((1<<(64-shift))-1))&MASK if shift else 0
 return (old&keep)|(word>>shift)
for start in range(8):
 mem=bytes((i*37+11)&255 for i in range(32))
 old=0xC4D3E2F101234567
 left_addr=start+7
 right_addr=start
 wl=int.from_bytes(mem[left_addr&~7:(left_addr&~7)+8],"little")
 wr=int.from_bytes(mem[right_addr&~7:(right_addr&~7)+8],"little")
 actual=ldr(ldl(old,wl,left_addr&7),wr,right_addr&7)
 expected=int.from_bytes(mem[start:start+8],"little")
 assert actual==expected,(start,hex(actual),hex(expected))
 # Verify reverse ordering is also valid for paired merge operations.
 assert ldl(ldr(old,wr,right_addr&7),wl,left_addr&7)==expected
print("Build 075 LDL/LDR: 8 alignments x 2 instruction orders passed")
