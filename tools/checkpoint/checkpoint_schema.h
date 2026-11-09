#ifndef PS2_CHECKPOINT_SCHEMA_H
#define PS2_CHECKPOINT_SCHEMA_H
#include "machine_state_stream.h"
namespace ps2state {
// Sections needed before a checkpoint can be considered a restorable machine.
// This gate intentionally rejects partial diagnostic-only state captures.
enum SectionId {
 EE_CPU=0x45454350u, EE_RAM=0x4545524du, EE_SCRATCH=0x45455343u,
 IOP_CPU=0x494f4350u, IOP_RAM=0x494f524du,
 SIF_STATE=0x53494653u, DMAC_STATE=0x444d4143u,
 INTC_STATE=0x494e5443u, TIMER_STATE=0x54494d52u,
 GS_STATE=0x47535354u, GIF_STATE=0x47494653u,
 VIF_STATE=0x56494653u, VU_STATE=0x56555354u,
 SPU_STATE=0x53505553u, CDVD_STATE=0x43445644u,
 INPUT_STATE=0x494e5054u
};
// Required section presence is necessary but NOT sufficient for a safe restore.
// A section containing one dummy byte must never count as valid CPU or RAM state.
static inline size_t minimum_section_size(uint32_t id){
 switch(id){
 case EE_RAM: return 32u*1024u*1024u;
 case IOP_RAM: return 2u*1024u*1024u;
 case EE_SCRATCH: return 16u*1024u;
 case EE_CPU: return 256u;
 case IOP_CPU: return 128u;
 default: return 2u;
 }
}
static inline bool complete(const std::vector<Section>&sections){
 static const uint32_t required[]={
 EE_CPU,EE_RAM,EE_SCRATCH,IOP_CPU,IOP_RAM,SIF_STATE,
 DMAC_STATE,INTC_STATE,TIMER_STATE,GS_STATE,GIF_STATE,
 VIF_STATE,VU_STATE,SPU_STATE,CDVD_STATE,INPUT_STATE
 };
 for(size_t i=0;i<sizeof(required)/sizeof(required[0]);i++){
  bool found=false;
  for(size_t j=0;j<sections.size();j++){
   if(sections[j].id==required[i]&&sections[j].bytes.size()>=minimum_section_size(required[i])){found=true;break;}
  }
  if(!found)return false;
 }
 return true;
}
}
#endif
