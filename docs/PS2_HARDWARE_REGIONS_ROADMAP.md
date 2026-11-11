# PS2 hardware-region implementation roadmap

Goal: implement PS2 hardware behavior rather than per-address diagnostic latches. This is a coverage plan, **not** a claim that the devices already work.

## Required architecture
- One physical address decoder per bus (EE, IOP), with explicit RAM/ROM/mirror/device regions, access-width and alignment handling, endian semantics, and unmapped faults.
- Device register definitions separated from device behavior. Read/write callbacks must account for masks, read-only bits, write-one-to-clear bits, reset values and side effects.
- Shared scheduler: EE, IOP, DMA, interrupt, timers, FIFOs and devices progress in emulated time. CPU stalls and interrupts must be observable.
- No fabricated SIF completion values or silent acceptance of unknown MMIO writes.
- Per-region diagnostic counters and traceable first fault with PC, opcode, VA, PA, access width, read/write, register value and branch-delay state.
- Automated register/memory tests and BIOS regression tests for every implemented device.

## Device groups
1. EE memory, EE scratchpad, BIOS ROM, address translation, EE memory controller and bus errors.
2. IOP RAM, mirrors, ROM, scratchpad/cache control, IOP memory controller and bus errors.
3. IOP and EE interrupt controllers, CPU exception/interrupt delivery, timers and scheduling.
4. EE SIF and IOP SIF shared registers, FIFOs, RPC transport, DMA and handshake.
5. EE DMAC and IOP DMAC, arbitration, transfer modes, completion and interrupt behavior.
6. CDVD controller, drive state, disc reads, DMA, boot media.
7. SIO2 and controllers/memory cards.
8. SPU2 registers, sound RAM, DMA and audio.
9. DEV9 and expansion bus, network and HDD interfaces where applicable.
10. USB OHCI and device interfaces.
11. GS, GIF, VIF0/1, VU0/1, IPU, video timing and rendering.
12. Remaining documented and BIOS-observed registers, with provenance and validation.

## Immediate Build 145 investigation
Latest Build 144 trace:
- IOP PC BFC4D384, instruction A1C40000 = SB R4,0(R14).
- VA/PA 1FA00000, R14=1FA00000, R4=0000000F, byte=0F.
- IOP stopped on unmapped byte write.
- EE PC 80005F14 polls SIF F230; zero reads=129733; watchdog stops after 17,000,000 EE instructions.
- Build 144 reports IOP RAM/BIOS accesses and diagnostic latches; this does not establish actual hardware semantics.

First verify the 0x1FA00000 physical region against PS2 hardware references and BIOS behavior, including bus ownership, mapping/aliasing, access sizes and expected side effects. Then implement a region-level device with tests, not an isolated special-case response. Verify SIF state transitions with both CPUs running. Do not assume the 0x1FA00000 write itself completes the SIF handshake.

## Definition of done per region
- All documented offsets and access widths represented, unknown offsets rejected or modeled as open bus only with evidence.
- Reset and state persistence semantics specified.
- Reads/writes and side effects verified against documentation, test ROMs or measured behavior.
- Interrupt and DMA effects implemented where relevant.
- Trace and unit tests included; BIOS progression verified without artificial success values.

## Important limitation
Full PS2 hardware compatibility is a multi-stage implementation effort. A mapped register with storage-only readback is not an emulated peripheral. The current emulator remains an experimental bring-up environment until the functional devices, scheduler and guest CPU semantics are sufficiently complete.
