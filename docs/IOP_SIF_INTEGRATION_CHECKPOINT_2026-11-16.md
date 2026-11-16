# IOP/SIF integration checkpoint — 16 November 2026

## Verified from repository scripts

- Build 077 introduces EE F240 storage without IOP handshake/interrupt effects.
- Build 081 introduces EE F200/F220 storage without IOP/DMA effects.
- Build 082 introduces EE F230 storage without IOP effects.
- Build 138 changes F220 writes to OR on the F220 value, and F230 writes to AND-NOT on the *separate F230 value*. This does **not** implement a shared EE/IOP SIF bridge.
- Build 137 detects repeated zero F230 reads while IOP and SIF writes are idle; it does not establish the root cause of a stall.
- Build 133 has a strict whitelist of observed IOP boot-register diagnostic latches; it is not a complete bus implementation.
- Build 157 emits a bounded pre-execution IOP fault window.

## Important correction to the first regression model

The initial standalone contract model incorrectly combined F220 and F230 into one flag value. The corrected `tools/tests/test_sif_sbus_contract.py` models two independent EE-side values. This is only a reference model; passing its tests cannot establish that the emulator's `Core::mmioRead/mmioWrite` works.

## Blocker to direct integration

The repository's default branch provides a Build 035 source **ZIP** plus sequential scripts. The current source directory referenced by the scripts (`src/PS2-PS3-Bringup-035-SOURCE`) is not exposed as ordinary source files in the repository. The GitHub text-file connector cannot read the ZIP as a source tree. Consequently, the generated latest `emu_core.cpp` has not been examined or compiled in this audit.

## Safe next implementation

1. Make the Build 035 archive contents accessible as ordinary source files, or extract the archive in a CI job that has it.
2. Determine the exact ordered patch chain and reconstruct generated sources in a clean worktree. Stop on the first missing anchor; do not skip scripts silently.
3. Identify authoritative storage for EE F200/F210/F220/F230/F240 and IOP 0x1D000000-region aliases, using PCSX2 hardware implementation as reference.
4. Add *integration* tests invoking actual `Core::mmioRead/mmioWrite` and IOP bus dispatch. Check independent F220/F230 semantics, shared visibility for the correct documented aliases, reset, and unhandled access.
5. Verify SIF0/SIF1 DMA ordering and interrupt acknowledgement separately; do not synthesize ready flags or return success from unsupported operations.
6. Compare BIOS traces against baseline, including first diverging PC, IOP retired count, register histories and watchdog reason.
7. Keep changes on a research branch until host tests, PS3 compilation and real-hardware boot checks pass.

## Status

Research/test-only change. No emulator MMIO patch, ELF, SELF, PKG, BIOS progress or real PS3 validation is claimed.
