#ifndef PS2_PS3_ACCELERATION_INI_H
#define PS2_PS3_ACCELERATION_INI_H
#include "acceleration_config.h"
#include <stdio.h>
#include <string.h>
namespace ps2accel {
// Only interpreter-only configuration is supported by this runtime build.
// Never change or truncate unrelated existing config.ini fields.
static inline bool load_ini(const char*path,Config&out){
 if(!path)return false;
 FILE*f=fopen(path,"rb");if(!f)return false;
 Config next;char line[512];unsigned mask=0;bool ok=true;
 while(fgets(line,sizeof(line),f)){
  if(!strchr(line,'\n')&&!feof(f)){ok=false;break;}
  const char*keys[]={"ee_backend=","iop_backend=","vu_backend=","spu_scheduling="};
  for(unsigned i=0;i<4;++i){
   const size_t n=strlen(keys[i]);
   if(strncmp(line,keys[i],n)==0){
    if(mask&(1u<<i)){ok=false;break;}
    mask|=1u<<i;
    const char*value=line+n;
    const char*expected=i==3?"disabled\n":"interpreter\n";
    if(strcmp(value,expected)!=0){ok=false;break;}
   }
  }
  if(!ok)break;
 }
 if(ferror(f))ok=false;
 fclose(f);
 if(!ok||mask!=15u)return false;
 out=next;return true;
}
static inline bool ensure_ini(const char*path){
 if(!path)return false;
 FILE*f=fopen(path,"rb");
 bool present[4]={false,false,false,false};
 if(f){
  char line[512];
  while(fgets(line,sizeof(line),f)){
   if(!strchr(line,'\n')&&!feof(f)){fclose(f);return false;}
   const char*keys[]={"ee_backend=","iop_backend=","vu_backend=","spu_scheduling="};
   for(unsigned i=0;i<4;++i){
    size_t n=strlen(keys[i]);
    if(strncmp(line,keys[i],n)==0){
     if(present[i]){fclose(f);return false;}
     present[i]=true;
     const char*expected=i==3?"disabled\n":"interpreter\n";
     if(strcmp(line+n,expected)!=0){fclose(f);return false;}
    }
   }
  }
  if(ferror(f)){fclose(f);return false;}
  fclose(f);
 }
 bool missing=false;for(unsigned i=0;i<4;++i)if(!present[i])missing=true;
 if(!missing)return true;
 f=fopen(path,"ab");if(!f)return false;
 const char*entries[]={"ee_backend=interpreter\n","iop_backend=interpreter\n","vu_backend=interpreter\n","spu_scheduling=disabled\n"};
 bool ok=true;
 for(unsigned i=0;i<4;++i)if(!present[i]&&fputs(entries[i],f)<0)ok=false;
 if(fclose(f)!=0)ok=false;
 return ok;
}
}
#endif
