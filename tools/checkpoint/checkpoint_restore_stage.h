#ifndef PS2_CHECKPOINT_RESTORE_STAGE_H
#define PS2_CHECKPOINT_RESTORE_STAGE_H
// Build 113: prepare/validate a checkpoint without mutating live emulation.
// This does NOT perform machine restore; device-specific restore hooks are pending.
#include "checkpoint_schema.h"
#include <vector>
namespace ps2state {
struct RestoreStage {
 std::vector<Section> sections;
 bool ready;
 RestoreStage():ready(false){}
 void clear(){sections.clear();ready=false;}
 const Section* find(uint32_t id) const {
  if(!ready)return NULL;
  for(size_t i=0;i<sections.size();++i)
   if(sections[i].id==id)return &sections[i];
  return NULL;
 }
};
// The caller must quiesce all guest execution before applying a prepared stage.
// Never apply a partially decoded checkpoint.
static inline bool prepare_restore(const void*data,size_t len,RestoreStage&stage){
 std::vector<Section> decoded;
 if(!decode(data,len,decoded)||!complete(decoded)){
  stage.clear();return false;
 }
 stage.sections.swap(decoded);
 stage.ready=true;
 return true;
}
}
#endif
