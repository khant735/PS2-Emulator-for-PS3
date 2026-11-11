#include "acceleration_ini.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
using namespace ps2accel;
int main(){
 const char*p="/tmp/ps2-acceleration-config-test.ini";
 remove(p);
 assert(ensure_ini(p));Config c;
 assert(load_ini(p,c)&&is_interpreter_only(c));
 assert(ensure_ini(p));
 FILE*f=fopen(p,"rb");assert(f);char data[1024]={0};size_t n=fread(data,1,sizeof(data)-1,f);fclose(f);
 assert(n==strlen("ee_backend=interpreter\niop_backend=interpreter\nvu_backend=interpreter\nspu_scheduling=disabled\n"));
 f=fopen(p,"wb");assert(f);
 assert(fputs("bios=/some/existing/path\ncustom=value\nee_backend=interpreter\n",f)>=0);
 assert(fclose(f)==0);
 assert(ensure_ini(p));f=fopen(p,"rb");assert(f);
 n=fread(data,1,sizeof(data)-1,f);data[n]=0;fclose(f);
 assert(strstr(data,"bios=/some/existing/path\ncustom=value\n") == data);
 assert(load_ini(p,c));
 f=fopen(p,"wb");assert(f);assert(fputs("ee_backend=dynarec\n",f)>=0);assert(fclose(f)==0);
 assert(!ensure_ini(p));assert(!load_ini(p,c));
 remove(p);
 puts("Build156 config.ini: safe interpreter defaults, idempotent append, existing keys preserved, unsupported backends rejected PASS");
}
