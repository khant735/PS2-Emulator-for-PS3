#!/usr/bin/env python3
"""Test SDL/SDR little-endian paired writes and untouched adjacent bytes."""
def store(mem,addr,value,left):
 offset=addr&7
 aligned=addr&~7
 for i in range(8):
  if (i<=offset if left else i>=offset):
   src=i+7-offset if left else i-offset
   mem[aligned+i]=(value>>(8*src))&255
for start in range(8,16):
 for reverse in (False,True):
  mem=bytearray([0xA5]*32)
  value=0x0123456789ABCDEF
  ops=[(start+7,True),(start,False)]
  if reverse:ops.reverse()
  for addr,left in ops:store(mem,addr,value,left)
  assert mem[start:start+8]==value.to_bytes(8,"little"),(start,reverse,mem.hex())
  assert mem[:start]==bytes([0xA5]*start)
  assert mem[start+8:]==bytes([0xA5]*(32-start-8))
print("Build 076 SDL/SDR: 8 alignments x 2 orders and surrounding bytes passed")
