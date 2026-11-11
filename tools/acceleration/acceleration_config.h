#ifndef PS2_PS3_ACCELERATION_CONFIG_H
#define PS2_PS3_ACCELERATION_CONFIG_H
// Build 155: safe, interpreter-only acceleration contract.
// This stage does not enable executable memory, a JIT or SPU workers.
namespace ps2accel {
enum CpuBackend { CPU_INTERPRETER=0, CPU_DYNAREC=1 };
enum VuBackend { VU_INTERPRETER=0, VU_RECOMPILER=1, VU_SPU_ASSISTED=2 };
enum SpuScheduling { SPU_DISABLED=0, SPU_AUTOMATIC=1 };
struct Capabilities {
 bool ee_jit, iop_jit, vu_jit, vu_spu, spu_workers;
 Capabilities():ee_jit(false),iop_jit(false),vu_jit(false),vu_spu(false),spu_workers(false){}
};
struct Config {
 CpuBackend ee,iop;
 VuBackend vu;
 SpuScheduling spu;
 Config():ee(CPU_INTERPRETER),iop(CPU_INTERPRETER),vu(VU_INTERPRETER),spu(SPU_DISABLED){}
};
static inline bool valid(const Config&c,const Capabilities&caps){
 if(c.ee!=CPU_INTERPRETER && c.ee!=CPU_DYNAREC)return false;
 if(c.iop!=CPU_INTERPRETER && c.iop!=CPU_DYNAREC)return false;
 if(c.vu!=VU_INTERPRETER && c.vu!=VU_RECOMPILER && c.vu!=VU_SPU_ASSISTED)return false;
 if(c.spu!=SPU_DISABLED && c.spu!=SPU_AUTOMATIC)return false;
 if(c.ee==CPU_DYNAREC&&!caps.ee_jit)return false;
 if(c.iop==CPU_DYNAREC&&!caps.iop_jit)return false;
 if(c.vu==VU_RECOMPILER&&!caps.vu_jit)return false;
 if(c.vu==VU_SPU_ASSISTED&&(!caps.vu_spu||!caps.spu_workers))return false;
 if(c.spu==SPU_AUTOMATIC&&!caps.spu_workers)return false;
 if(c.vu==VU_SPU_ASSISTED&&c.spu==SPU_DISABLED)return false;
 return true;
}
// Fail closed to the known-safe interpreter configuration.
static inline Config resolve(const Config&requested,const Capabilities&caps){
 return valid(requested,caps)?requested:Config();
}
static inline bool is_interpreter_only(const Config&c){
 return c.ee==CPU_INTERPRETER&&c.iop==CPU_INTERPRETER&&c.vu==VU_INTERPRETER&&c.spu==SPU_DISABLED;
}
}
#endif
