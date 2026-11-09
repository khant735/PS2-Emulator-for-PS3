#include "machine_state_stream.h"
#include "checkpoint_schema.h"
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
 assert(!ps2state::complete(decoded)); // Never resume a partial snapshot.
 const uint32_t ids[]={ps2state::EE_CPU,ps2state::EE_RAM,ps2state::EE_SCRATCH,
 ps2state::IOP_CPU,ps2state::IOP_RAM,ps2state::SIF_STATE,ps2state::DMAC_STATE,
 ps2state::INTC_STATE,ps2state::TIMER_STATE,ps2state::GS_STATE,
 ps2state::GIF_STATE,ps2state::VIF_STATE,ps2state::VU_STATE,
 ps2state::SPU_STATE,ps2state::CDVD_STATE,ps2state::INPUT_STATE};
 std::vector<ps2state::Section> all;
 for(size_t i=0;i<sizeof(ids)/sizeof(ids[0]);++i){
  ps2state::Section sec;sec.id=ids[i];sec.bytes.push_back((unsigned char)(i+1));
  all.push_back(sec);
 }
 assert(ps2state::complete(all));
 for(size_t i=0;i<all.size();++i){
  std::vector<ps2state::Section> missing=all;
  missing.erase(missing.begin()+i);
  assert(!ps2state::complete(missing));
 }
 all[0].bytes.clear();
 assert(!ps2state::complete(all));

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
