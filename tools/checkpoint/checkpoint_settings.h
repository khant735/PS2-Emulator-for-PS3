#ifndef PS2_CHECKPOINT_SETTINGS_H
#define PS2_CHECKPOINT_SETTINGS_H
// Save-state compression preferences. Independent of emulator restore support.
#include <stdio.h>
#include <string.h>
namespace ps2checkpoint {
enum CompressionType { DEFLATE=1 };
struct CompressionSettings {
 int type;
 int level;
 CompressionSettings():type(DEFLATE),level(1){}
 bool valid() const {return type==DEFLATE&&level>=0&&level<=9;}
};
static inline bool save_compression_settings(const char*path,const CompressionSettings&v){
 if(!path||!v.valid())return false;
 char tmp[1024];
 if(strlen(path)>sizeof(tmp)-5)return false;
 snprintf(tmp,sizeof(tmp),"%s.tmp",path);
 FILE*f=fopen(tmp,"wb");if(!f)return false;
 bool ok=fprintf(f,"save_state_compression=deflate\nsave_state_level=%d\n",v.level)>0;
 if(fclose(f)!=0)ok=false;
 if(ok)ok=rename(tmp,path)==0;
 if(!ok)remove(tmp);
 return ok;
}
static inline bool load_compression_settings(const char*path,CompressionSettings&out){
 if(!path)return false;
 FILE*f=fopen(path,"rb");if(!f)return false;
 char line[128];CompressionSettings next;bool type_seen=false,level_seen=false,ok=true;
 while(fgets(line,sizeof(line),f)){
  if(!strchr(line,'\n')&&!feof(f)){ok=false;break;}
  if(strncmp(line,"save_state_compression=",23)==0){
   if(type_seen||strcmp(line+23,"deflate\n")!=0){ok=false;break;}
   type_seen=true;
  }else if(strncmp(line,"save_state_level=",17)==0){
   if(level_seen||line[17]<'0'||line[17]>'9'||(line[18]!='\n'&&line[18]!='\0')){ok=false;break;}
   next.level=line[17]-'0';level_seen=true;
  }else if(line[0]!='#'&&line[0]!='\n'){ok=false;break;}
 }
 if(ferror(f))ok=false;
 fclose(f);
 if(!ok||!type_seen||!level_seen||!next.valid())return false;
 out=next;return true;
}
}
#endif
