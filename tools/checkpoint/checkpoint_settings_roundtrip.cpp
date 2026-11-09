#include "checkpoint_settings.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
int main(){
 const char*path="/tmp/ps2-checkpoint-settings-test.ini";
 for(int level=0;level<=9;++level){
  ps2checkpoint::CompressionSettings a,b;
  a.level=level;b.level=9-level;
  assert(ps2checkpoint::save_compression_settings(path,a));
  assert(ps2checkpoint::load_compression_settings(path,b));
  assert(b.type==ps2checkpoint::DEFLATE&&b.level==level);
 }
 ps2checkpoint::CompressionSettings invalid;invalid.level=10;
 assert(!ps2checkpoint::save_compression_settings(path,invalid));
 invalid.level=-1;assert(!ps2checkpoint::save_compression_settings(path,invalid));
 FILE*f=fopen(path,"wb");assert(f);
 assert(fputs("save_state_compression=deflate\nsave_state_level=99\n",f)>=0);
 assert(fclose(f)==0);
 ps2checkpoint::CompressionSettings keep;keep.level=4;
 assert(!ps2checkpoint::load_compression_settings(path,keep));
 assert(keep.level==4);
 remove(path);
 puts("Checkpoint compression preferences: levels 0-9, persistence and invalid input PASS");
}
