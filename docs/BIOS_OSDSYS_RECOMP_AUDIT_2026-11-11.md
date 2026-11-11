# PS2 BIOS / OSDSYS / recompilation research audit (11 Nov 2026)

## Purpose
Use independently implemented PS2 BIOS, PCSX2-derived emulation, OSDSYS decompilation and static recompilers to close correctness gaps in the PS3 PowerPC emulator. This document distinguishes source observations from hypotheses. No game or Sony BIOS binaries are included.

## Confirmed local code issue: SIF F230
- `tools/build082_sif_f230.py` installs an **experimental storage-only** handler for EE address `0x1000F230`. It writes `ee_sif_f230=uint32_t(v)` and comments `no IOP handshake or status synthesis`.
- In ARMSX2/PCSX2 `pcsx2/HwWrite.cpp`, `SBUS_F220` performs atomic OR (set bits), while `SBUS_F230` performs atomic AND with the complement of the written value (clear bits). `pcsx2/HwRead.cpp` reads the shared register state and calls `IopThread::EeSbusNearBound`.
- PCSX2 comments state that the IOP accesses the same SBUS words via the `0x1D000000` window. Thus EE-only F230 storage cannot model the complete handshake.
- `tools/build137_adaptive_watchdog.py` only detects repeated zero F230 reads while IOP progress and F230 writes stop; it does not provide the missing SIF functionality.

**Important caveat:** Build scripts are historical transformations; verify the *current* generated `emu_core.cpp` and any later patches before asserting the latest binary still has the exact Build 082 implementation.

### Proposed implementation (not yet applied)
1. Locate the authoritative EE and IOP SBUS register storage in current source. Avoid adding duplicate state.
2. Map EE `0x1000F200/F210/F220/F230/F240` and corresponding IOP `0x1D000000` aliases to shared state; verify exact IOP offsets from a hardware reference and current BIOS traces.
3. Implement documented set/clear semantics for F220/F230; preserve F240 control/interrupt side effects separately.
4. Keep EE and IOP cycle accounting coherent; don't fabricate IOP-ready flags.
5. Add unit tests for shared visibility, set/clear writes, reset state, aliasing, IRQ behavior and DMA ordering.
6. Run the existing BIOS trace with a *bounded* adaptive watchdog; compare IOP instruction count, first failing PC, F230 read/write history and SIF DMA events.
7. Only after a functional advance, add the fix to the PS3 build; preserve the previous known-working build.

## Source map and licensing

| Project | Useful source | What it provides | Important limitation |
| --- | --- | --- | --- |
| [ARMSX2](https://github.com/ARMSX2/ARMSX2) (PCSX2-derived) | `pcsx2/HwRead.cpp`, `HwWrite.cpp`, `Sif0.cpp`, `Sif1.cpp`, `IopDma.cpp` | Shared SBUS, DMA FIFOs, interrupts, EE/IOP timing | ARM64 JIT not directly executable on PS3 PowerPC; review upstream license |
| [OpenPS2BIOS](https://github.com/TamaribaEmu/OpenPS2BIOS) | `src/ee/sif.c`, `src/iop/sif.c`, `src/common/sifdma.c`, `src/iop/loadcore.c` | Open BIOS-side initialization and services | Replacement BIOS, not Sony's original source |
| [fps2bios](https://github.com/AKuHAK/fps2bios) | `doc/overview.md`, kernel/bootstrap sources | ROMDIR/RESET/IRX loading overview | Reported licensing uncertainty; reference only unless rights clarified |
| [biostation](https://github.com/ravenslofty/biostation) | EE bootstrap, GS, INTC/DMAC | Clean-room BIOS initialization reference | Incomplete |
| [CrystalOSD-Decomp-Legacy](https://github.com/JeanxPereira/CrystalOSD-Decomp-Legacy) | OSDSYS browser, CDVD, boot pipeline | Matching-decompilation style OSDSYS analysis | Not hardware emulation; check version match |
| [CrystalOSD](https://github.com/JeanxPereira/CrystalOSD) | OSD graphics and boot documentation | UI/OSD behaviour | Native recreation, not PS2 CPU emulation |
| [PS2 Web Recomp](https://github.com/snuri00/ps2-web-recomp) | `recomp/`, `runtime/src/iop/cpu.cpp`, `runtime/src/hw.cpp`, `runtime/src/dmac.cpp` | EE-to-C++ static recompilation, IOP interpreter, GS/VU runtime | High-level EE kernel; browser/native host dependencies |
| [PS2Recomp](https://github.com/ran-j/PS2Recomp) | `ps2xRecomp`, `ps2xIOP`, `ps2xRuntime` | C++ R5900 output, IRX interpreter and SIF RPC | GPL-3.0, x86 SSE/AVX paths, incomplete hardware |
| [EmotionEngineDisassembler](https://github.com/TimoSalomaki/EmotionEngineDisassembler) | `PS2Disassembler.Core/Decoder` | Independent C790 opcode decoder | Incomplete VPU, no unit tests, potential decoding errors |

## BIOS module inventory: work not yet completed
Extract ROMDIR entries from a **user-supplied, legitimately obtained BIOS image** and record for each: BIOS revision/hash, ROMDIR name/offset/size, executable format, EE/IOP target, entry point, imports/exports, module dependencies, initialization MMIO, source-reference match, and trace evidence. No inventory is claimed without examining the actual BIOS image.

Priority modules where present: RESET, ROMDIR, IOPLOAD, LOADCORE, SYSMEM, SIFMAN, SIFCMD, CDVDMAN and OSDSYS. Different BIOS revisions may differ.

## Recompilation investigation
- Both PS2 Web Recomp and PS2Recomp generate C++ from R5900 code, which suggests an experimental PS3DEV PPU compilation path.
- This is not a drop-in general-purpose BIOS emulator. Generated code requires guest memory mapping, instruction semantics, runtime services, and replacements for unsupported graphics/audio/host APIs.
- Build a minimal MIPS EE ELF instruction conformance harness first; compare interpreter and recompiled output before porting whole games.
- Separate independently written clean-room hardware implementations from copied GPL-licensed code and document attribution/compatibility before integrating.

## Validation gates
1. Host-side regression tests pass.
2. PS3 cross-compilation and packaging succeed.
3. Real PS3 boot does not regress UI, settings, storage paths or logging.
4. SIF/IOP test demonstrates a real transition, not a synthetic ready bit.
5. BIOS traces demonstrate new executed instructions or module progress, rather than merely a higher instruction cap.
6. Each release retains signed SELF, ELF, PKG and source ZIP.

## Status
This is a source-grounded initial audit and prioritized implementation plan, **not** a claim that the current emulator has been modified or that the BIOS now boots.
