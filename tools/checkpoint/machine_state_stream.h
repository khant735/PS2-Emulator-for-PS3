#ifndef PS2_STATE_STREAM_H
#define PS2_STATE_STREAM_H
// Explicit, pointer-free machine-state section stream.
// This is a serialization primitive, not a complete Core snapshot.
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <vector>
namespace ps2state {
enum { STREAM_VERSION=1, MAX_STREAM_BYTES=128*1024*1024, MAX_SECTIONS=256 };
static inline void put32(std::vector<unsigned char>&v,uint32_t x){
 for(int i=0;i<4;i++)v.push_back((unsigned char)(x>>(8*i)));
}
static inline bool get32(const unsigned char*&p,const unsigned char*end,uint32_t&v){
 if((size_t)(end-p)<4)return false;
 v=(uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
 p+=4;return true;
}
struct Section { uint32_t id;std::vector<unsigned char> bytes; };
class Writer {
 std::vector<unsigned char> out;
 uint32_t count;
 bool valid;
public:
 Writer():count(0),valid(true){
  const char magic[8]={'P','2','M','A','C','H','0','1'};
  out.insert(out.end(),magic,magic+8);put32(out,STREAM_VERSION);
 }
 bool append(uint32_t id,const void*data,size_t len){
  if(!valid||!id||!data||!len||len>MAX_STREAM_BYTES||count>=MAX_SECTIONS
    ||out.size()>MAX_STREAM_BYTES-8-len)return valid=false;
  // Reject duplicate sections before writing.
  const unsigned char*p=&out[12],*end=&out[0]+out.size();
  while(p<end){uint32_t old=0,n=0;
   if(!get32(p,end,old)||!get32(p,end,n)||n>(size_t)(end-p))return valid=false;
   if(old==id)return valid=false;
   p+=n;
  }
  put32(out,id);put32(out,(uint32_t)len);
  const unsigned char*b=(const unsigned char*)data;
  out.insert(out.end(),b,b+len);++count;return true;
 }
 bool good()const{return valid&&count>0;}
 const std::vector<unsigned char>& bytes()const{return out;}
};
static inline bool decode(const void*data,size_t len,std::vector<Section>&dest){
 if(!data||len<20||len>MAX_STREAM_BYTES)return false;
 const unsigned char*p=(const unsigned char*)data,*end=p+len;
 if(memcmp(p,"P2MACH01",8))return false;p+=8;
 uint32_t version=0;if(!get32(p,end,version)||version!=STREAM_VERSION)return false;
 std::vector<Section> tmp;
 while(p<end){
  uint32_t id=0,n=0;
  if(tmp.size()>=MAX_SECTIONS||!get32(p,end,id)||!get32(p,end,n)
    ||!id||!n||n>(size_t)(end-p))return false;
  for(size_t i=0;i<tmp.size();i++)if(tmp[i].id==id)return false;
  Section s;s.id=id;s.bytes.assign(p,p+n);tmp.push_back(s);p+=n;
 }
 if(tmp.empty())return false;
 dest.swap(tmp);return true;
}
}
#endif
