#include "checkpoint_zlib.h"
#include <assert.h>
#include <stdio.h>
int main(){
 unsigned char bios[32]={0},other[32]={1};
 unsigned char before[8192],after[8192];
 for(size_t i=0;i<sizeof(before);++i)before[i]=(unsigned char)(i*i+17);
 memset(after,0,sizeof(after));
 assert(ps2checkpoint::write("/tmp/ps2-checkpoint-test.bin",before,sizeof(before),bios,101));
 assert(!ps2checkpoint::read("/tmp/ps2-checkpoint-test.bin",after,sizeof(after),other,101));
 assert(!ps2checkpoint::read("/tmp/ps2-checkpoint-test.bin",after,sizeof(after),bios,102));
 assert(ps2checkpoint::read("/tmp/ps2-checkpoint-test.bin",after,sizeof(after),bios,101));
 assert(memcmp(before,after,sizeof(before))==0);
 FILE* f=fopen("/tmp/ps2-checkpoint-test.bin","r+b");assert(f);
 assert(fseek(f,-1,SEEK_END)==0);fputc(0xFF,f);fclose(f);
 assert(!ps2checkpoint::read("/tmp/ps2-checkpoint-test.bin",after,sizeof(after),bios,101));
 remove("/tmp/ps2-checkpoint-test.bin");
 puts("Checkpoint container: roundtrip, BIOS/schema mismatch and corruption checks passed");
}
