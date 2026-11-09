#include "machine_state_stream.h"
#include "checkpoint_zlib.h"
#include <assert.h>
#include <stdio.h>
int main(){
 unsigned char ee[64],iop[48],bios[32]={0};
 for(size_t i=0;i<sizeof(ee);i++)ee[i]=(unsigned char)i;
 for(size_t i=0;i<sizeof(iop);i++)iop[i]=(unsigned char)(i*7);
 ps2state::Writer w;
 assert(w.append(0x45455247,ee,sizeof(ee)));
 assert(w.append(0x494F5052,iop,sizeof(iop)));
 assert(!w.append(0x45455247,ee,sizeof(ee)));
 assert(!w.good());
 ps2state::Writer good;
 assert(good.append(0x45455247,ee,sizeof(ee)));
 assert(good.append(0x494F5052,iop,sizeof(iop)));
 std::vector<ps2state::Section> decoded;
 assert(ps2state::decode(&good.bytes()[0],good.bytes().size(),decoded));
 assert(decoded.size()==2&&decoded[0].bytes.size()==sizeof(ee));
 assert(memcmp(&decoded[0].bytes[0],ee,sizeof(ee))==0);
 assert(memcmp(&decoded[1].bytes[0],iop,sizeof(iop))==0);
 std::vector<unsigned char> damaged=good.bytes();
 damaged[12]=0;damaged[13]=0;damaged[14]=0;damaged[15]=0;
 assert(!ps2state::decode(&damaged[0],damaged.size(),decoded));
 assert(decoded.size()==2);
 assert(ps2checkpoint::write("/tmp/ps2-machine-state.bin",&good.bytes()[0],good.bytes().size(),bios,1));
 std::vector<unsigned char> restored(good.bytes().size());
 assert(ps2checkpoint::read("/tmp/ps2-machine-state.bin",&restored[0],restored.size(),bios,1));
 assert(ps2state::decode(&restored[0],restored.size(),decoded));
 assert(decoded.size()==2);
 remove("/tmp/ps2-machine-state.bin");
 puts("Machine state stream: bounded sections, duplicate rejection, transactional decode, zlib roundtrip PASS");
}
