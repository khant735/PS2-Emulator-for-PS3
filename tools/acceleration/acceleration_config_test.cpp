#include "acceleration_config.h"
#include <assert.h>
#include <stdio.h>
using namespace ps2accel;
int main(){
 Capabilities none;
 Config defaults;
 assert(valid(defaults,none));
 assert(is_interpreter_only(defaults));
 Config request;
 request.ee=CPU_DYNAREC;
 assert(!valid(request,none));
 assert(is_interpreter_only(resolve(request,none)));
 request=Config();request.iop=CPU_DYNAREC;
 assert(!valid(request,none));
 request=Config();request.vu=VU_RECOMPILER;
 assert(!valid(request,none));
 request=Config();request.vu=VU_SPU_ASSISTED;
 assert(!valid(request,none));
 request=Config();request.spu=SPU_AUTOMATIC;
 assert(!valid(request,none));
 request=Config();request.ee=(CpuBackend)99;
 assert(!valid(request,none));
 request=Config();request.vu=(VuBackend)99;
 assert(!valid(request,none));
 request=Config();request.spu=(SpuScheduling)99;
 assert(!valid(request,none));
 Capabilities enabled;
 enabled.ee_jit=true;enabled.iop_jit=true;enabled.vu_jit=true;
 enabled.vu_spu=true;enabled.spu_workers=true;
 request=Config();request.ee=CPU_DYNAREC;
 assert(valid(request,enabled));
 assert(resolve(request,enabled).ee==CPU_DYNAREC);
 request=Config();request.vu=VU_SPU_ASSISTED;request.spu=SPU_AUTOMATIC;
 assert(valid(request,enabled));
 request.spu=SPU_DISABLED;
 assert(!valid(request,enabled));
 puts("Build155 acceleration contract: interpreter defaults, unsupported backends rejected, fallback and capability gating PASS");
}
