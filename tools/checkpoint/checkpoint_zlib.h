#ifndef PS2_CHECKPOINT_ZLIB_H
#define PS2_CHECKPOINT_ZLIB_H
// Development checkpoint container. Caller must serialize *all* emulated state.
// Does not serialize host pointers or handles. Does not enable unsafe partial restores.
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zlib.h>
namespace ps2checkpoint {
enum { VERSION=1, MAX_PAYLOAD=128*1024*1024 };
struct Header {
 unsigned char magic[8];
 uint32_t version, raw_size, compressed_size, raw_crc32;
 unsigned char bios_sha256[32];
 uint32_t state_schema;
};
static inline bool write_with_level(const char* path,const void* data,size_t size,const unsigned char bios[32],uint32_t schema,int level) {
 // DEFLATE levels 0 (store) through 9 (maximum); reject invalid settings.
 if(level<0||level>9)return false;
 if(!path||!data||!bios||!schema||size==0||size>MAX_PAYLOAD) return false;
 uLongf bound=compressBound((uLong)size);
 Bytef* packed=(Bytef*)malloc(bound);
 if(!packed) return false;
 uLongf len=bound;
 int rc=compress2(packed,&len,(const Bytef*)data,(uLong)size,level);
 if(rc!=Z_OK||len>UINT32_MAX){free(packed);return false;}
 Header h={}; memcpy(h.magic,"P2STATE1",8);h.version=VERSION;
 h.raw_size=(uint32_t)size;h.compressed_size=(uint32_t)len;
 h.raw_crc32=(uint32_t)crc32(crc32(0L,Z_NULL,0),(const Bytef*)data,(uInt)size);
 memcpy(h.bios_sha256,bios,32);h.state_schema=schema;
 // Write to a temporary file, then rename after all writes succeed.
 size_t n=strlen(path);char* tmp=(char*)malloc(n+5);
 if(!tmp){free(packed);return false;}
 memcpy(tmp,path,n);memcpy(tmp+n,".tmp",5);
 FILE* f=fopen(tmp,"wb");
 bool ok=f && fwrite(&h,1,sizeof(h),f)==sizeof(h) && fwrite(packed,1,len,f)==len;
 if(f && fclose(f)!=0)ok=false;
 if(ok){ok=rename(tmp,path)==0;}
 if(!ok)remove(tmp);
 free(tmp);free(packed);return ok;
}
static inline bool write(const char* path,const void* data,size_t size,const unsigned char bios[32],uint32_t schema) {
 return write_with_level(path,data,size,bios,schema,1);
}
static inline bool read(const char* path,void* output,size_t expected_size,const unsigned char bios[32],uint32_t schema) {
 if(!path||!output||!bios||!schema||expected_size==0||expected_size>MAX_PAYLOAD)return false;
 FILE* f=fopen(path,"rb");if(!f)return false;
 Header h={};
 bool ok=fread(&h,1,sizeof(h),f)==sizeof(h);
 ok=ok&&memcmp(h.magic,"P2STATE1",8)==0&&h.version==VERSION
   &&h.raw_size==expected_size&&h.compressed_size>0&&h.compressed_size<=MAX_PAYLOAD
   &&h.state_schema==schema&&memcmp(h.bios_sha256,bios,32)==0;
 Bytef* packed=ok?(Bytef*)malloc(h.compressed_size):NULL;
 Bytef* raw=ok?(Bytef*)malloc(expected_size):NULL;
 ok=ok&&packed&&raw;
 if(ok)ok=fread(packed,1,h.compressed_size,f)==h.compressed_size && fgetc(f)==EOF;
 fclose(f);
 if(ok){uLongf n=(uLongf)expected_size;
   ok=uncompress(raw,&n,packed,h.compressed_size)==Z_OK&&n==expected_size;
   if(ok)ok=(uint32_t)crc32(crc32(0L,Z_NULL,0),raw,(uInt)n)==h.raw_crc32;
   if(ok)memcpy(output,raw,expected_size);
 }
 free(packed);free(raw);return ok;
}
}
#endif
