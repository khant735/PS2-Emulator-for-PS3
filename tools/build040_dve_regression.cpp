#include "ee_dve.h"
#include <cassert>
#include <cstdint>
int main(){
 EeDve d; d.reset();
 // Reproduce the BIOS mode 0x43 / command 0x81 sequence.
 assert(d.write(6,3));
 assert(d.write(2,0x43));
 assert(d.write(0,0x81));
 assert(d.active && d.commands==1 && !d.error);
 assert(!d.selected && !d.known[0]);
 // Unsupported commands must remain rejected.
 assert(!d.write(0,0x83));
 // Existing mode 43 selector+data behaviour is preserved.
 assert(d.write(16,0x7e));assert(d.write(18,0x55));
 assert(d.write(0,0x82));
 assert(d.selected && d.known[0x7e] && d.device[0x7e]==0x55);
 // Mode 42 can retrieve the previously selected register.
 assert(d.write(2,0x42));assert(d.write(0,0x81));
 assert(d.bus[8]==0x55);
 return 0;
}
