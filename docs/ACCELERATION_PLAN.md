# PS2 Emulator for PS3 — acceleration development contract (Build 155)

## Current selected configuration

- EE: interpreter
- IOP: interpreter
- VU0/VU1: interpreter
- SPU scheduling: disabled

Build 155 introduces a **host-testable capability contract**, not an executable JIT or SPU worker. The existing PS3 runtime is unchanged. The contract deliberately advertises no acceleration capabilities, and unsupported requests resolve to interpreter-only defaults. There are no firmware patches, executable-memory mappings, SPU jobs, or new in-app settings in this stage.

## Follow-up stages

1. Preserve Build 154 BIOS/IOP diagnostics and correct guest execution using traces.
2. Integrate this contract into the emulator runtime and persisted settings, still interpreter-only; verify real PS3 boot and config compatibility.
3. Prototype a separately tested native PPU code-cache/JIT with memory permissions, instruction-cache synchronization, guest code invalidation, exceptions and deterministic interpreter comparison.
4. Prototype SPU workers in isolation, with correctness and transfer-cost benchmarks; enable only when supported and measured faster.
5. Expose selectable settings only for backends that actually exist, retaining interpreter fallback.

The SPUs run a different ISA from the PPU and cannot execute PPU-generated native code. ManaGunZ's Dynarec payload is an executable-memory permission patch, not a PS2 MIPS-to-PPU compiler. Do not blindly reuse its firmware-specific LV2 patches.
