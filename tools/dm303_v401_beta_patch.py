#!/usr/bin/env python3
"""Create a direct DM303 V4.0.1 beta firmware candidate.

This patcher does not modify the source firmware in place. It emits a new
candidate binary and a byte-level report so every change can be audited before
any device-side test.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


SOURCE = Path("backup/DM303 V4.0-read only/DM303V4.004.bin")
MS_TEXT = Path("localization/ms_MY/TEXT_MS.DAT")
SP_TEXT = Path("localization/ms_MY/TEXT_SP.ms-slot-replacement.DAT")
SAFE_SP_TEXT = Path("localization/ms_MY/TEXT_SP.safe-slot-replacement.DAT")
OUT_DIR = Path("firmware-candidates/v4.0.1-beta")
OUT_BIN = OUT_DIR / "DM303V4.0.1-beta.bin"
OUT_SYSTEM = OUT_DIR / "system"
OUT_REPORT = OUT_DIR / "PATCH-REPORT.md"
OUT_SUMS = OUT_DIR / "SHA256SUMS.txt"

LOAD_BASE = 0x08010000
SOURCE_SHA256 = "64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158"
FAULT_BLOCK_OFFSET = 0x7554
FAULT_BLOCK_SIZE = 20
FAULT_STUB_VECTOR = 0x08017555
VECTOR_WORDS = 80

DEFAULT_PROFILE = "stability-exp20-ms-safe"
PROFILES = {
    "boot-acceptance": {
        "fault_reset": False,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "boot_logo_delay": False,
        "description": "minimal beta identity and resource build",
    },
    "anti-freeze-exp1": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "boot_logo_delay": False,
        "description": "reset on fault/default handler and return from known fail-stop loops",
    },
    "relay-settle-exp1": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": "exp1",
        "mode_switch_profile": None,
        "boot_logo_delay": False,
        "description": "anti-freeze plus longer relay/range settling delays for zeroing and mode changes",
    },
    "force-stable-exp2": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": "exp2",
        "mode_switch_profile": None,
        "boot_logo_delay": False,
        "description": "exp1 plus stronger relay/range settling for unstable AC/DC current switching",
    },
    "v316-switch-exp3": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": "v316-helper-wrapper",
        "boot_logo_delay": False,
        "description": "anti-freeze plus V3.16-style mode-switch helper wrapper with official relay timing",
    },
    "force-enhanced-exp4": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": "exp2",
        "mode_switch_profile": "v316-helper-wrapper",
        "boot_logo_delay": True,
        "description": "force-enhanced stability profile with V3.16 mode wrapper, stronger relay settling, and boot-logo stabilization delay",
    },
    "clean-stability-exp5": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "boot_logo_delay": True,
        "description": "clean stability profile with fault recovery, official relay timing, original mode helper, Malay UI resources, and boot-logo stabilization delay",
    },
    "stream-recovery-exp6": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-busy-retry",
        "low_io_timeout_profile": None,
        "boot_logo_delay": True,
        "description": "clean stability plus guarded fail-fast recovery for high-level measurement stream retry loops",
    },
    "stream-recovery-exp7": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-busy-retry",
        "low_io_timeout_profile": "half-timeout",
        "boot_logo_delay": True,
        "description": "exp6 plus guarded lower byte-IO timeout reduction for faster recovery after spike/overload stalls",
    },
    "stream-recovery-exp8": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-busy-retry",
        "low_io_timeout_profile": "tight-timeout",
        "command_retry_profile": None,
        "boot_logo_delay": True,
        "description": "exp7 fine-tune with tighter lower byte-IO timeout for lower recovery latency",
    },
    "stream-recovery-exp9": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-busy-retry",
        "low_io_timeout_profile": "tight-timeout",
        "command_retry_profile": "balanced-0x60",
        "boot_logo_delay": True,
        "description": "fail-fast stream/status recovery with tight byte-IO timeout and balanced command retry clamp",
    },
    "stream-recovery-exp10": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": "tight-timeout",
        "command_retry_profile": "balanced-0x60",
        "boot_logo_delay": True,
        "description": "exp9 timing with command-0x40 busy failure routed into the existing error/clear path",
    },
    "stream-recovery-exp11": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "boot_logo_delay": True,
        "description": "exp10 status recovery plus bounded low-IO failure return instead of stale reads after ready-timeout",
    },
    "stream-recovery-exp12": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "boot_logo_delay": True,
        "description": "exp11 plus guarded stream error-state clear for stale busy/status after spike or overload",
    },
    "stream-recovery-exp13": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "boot_logo_delay": True,
        "description": "exp12 plus guarded stale state clear at the mode/range entry before relay switching",
    },
    "stream-recovery-exp14": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640",
        "boot_logo_delay": True,
        "description": "exp13 plus forced stream transaction after stale busy and capped long current-switch gate for the reported AC-to-DC ammeter delay",
    },
    "stream-recovery-exp15": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640",
        "instant_switch_profile": "force-mode-call-immediate",
        "stale_error_gate_profile": "ignore-bit0-error-gates",
        "version_patch_profile": "visible-exp15",
        "boot_logo_delay": True,
        "description": "exp14 plus visible V4.0.1c marker, immediate mode-call gates, and stale bit0 error-gate bypass for the no-improvement field result",
    },
    "stream-recovery-exp16-ui-safe": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640",
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-exp16",
        "language_name_patch": False,
        "boot_logo_delay": False,
        "description": "exp14 recovery bytes with visible V4.0.1d marker, exp15 aggressive gates removed, and boot-logo delay disabled for UI/loading isolation",
    },
    "clean-resource-exp17": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": None,
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": None,
        "command_retry_profile": None,
        "stream_state_clear_profile": None,
        "mode_state_clear_profile": None,
        "stream_busy_gate_profile": None,
        "current_switch_latency_profile": None,
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-exp17",
        "language_name_patch": False,
        "boot_logo_delay": False,
        "description": "clean resource-restore build: official measurement/control flow, visible V4.0.1e marker, fault/fail-stop recovery only, and external DM30XDB1 resource restored by the final merge",
    },
    "stability-exp18-resource": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640",
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-exp18",
        "language_name_patch": False,
        "boot_logo_delay": False,
        "description": "exp18 resource-complete stability build: restore exp14/exp16 bounded recovery and AC-to-DC latency caps on top of the proven DM30XDB1-complete package, with UI/language slots kept official",
    },
    "stability-exp19-ui-ms": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640",
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-exp19",
        "language_name_patch": True,
        "boot_logo_delay": False,
        "description": "exp19 UI-restored stability build: keep exp18 bounded recovery and DM30XDB1 resource fix while re-enabling the Melayu/SP slot and safe dark resource pack",
    },
    "stability-exp20-ms-safe": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640",
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-exp20",
        "language_name_patch": True,
        "sp_text_source": "safe-sp-layout",
        "boot_logo_delay": False,
        "description": "exp20 safe Melayu SP build: keep exp18 bounded recovery and DM30XDB1 resource fix while using a Malay TEXT_SP rebuilt from the official SP 773-entry layout",
    },
    "v401h-repair-a": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640",
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-exp20",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "repair profile after V4.0.1h field failure: keep only the exp14/exp16 recovery core and V4.0.1h marker while removing Malay slot/resource and UI-theme changes for measurement isolation",
    },
    "v401h-repair-b": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640-plus-state2",
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-exp20",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "repair profile after repair-a showed no field change: keep UI/resources official and add the remaining state-2 current-switch latency caps in the same timing cluster",
    },
    "v401h-repair-c": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": "exp1",
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640-plus-state2",
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-c",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "measurement repair profile: repair-b latency/state recovery plus moderate vendor-path relay/mux settle timing for cleaner zeroing after physical switching",
    },
    "v401h-repair-d": {
        "fault_reset": True,
        "runtime_patches": True,
        "runtime_patch_profile": "no-ui-render-fallthrough",
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640-plus-state2",
        "instant_switch_profile": "force-mode-call-immediate",
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-d",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "repair after repair-c failed: remove relay-settle increase, keep official UI resources, exclude risky UI/render fail-stop fall-through, and test immediate current-switch mode calls",
    },
    "v401h-repair-e": {
        "fault_reset": True,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": "fail-fast-error-route",
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": "bounded-fail-0xfa0",
        "command_retry_profile": "balanced-0x60",
        "stream_state_clear_profile": "clear-error-and-stale-busy",
        "mode_state_clear_profile": "mode-range-clear-stale-busy",
        "stream_busy_gate_profile": "force-stream-transaction",
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640-plus-state2",
        "instant_switch_profile": "force-mode-call-immediate",
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-e",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "clean UI measurement candidate: keep official runtime fail-stop guards, official UI resources, repair-b current latency caps, and immediate mode/range calls",
    },
    "v401h-repair-f": {
        "fault_reset": False,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": None,
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": None,
        "command_retry_profile": None,
        "stream_state_clear_profile": None,
        "mode_state_clear_profile": None,
        "stream_busy_gate_profile": None,
        "current_switch_latency_profile": "cap-long-switch-gate-0x0640-plus-state2",
        "instant_switch_profile": "force-mode-call-immediate",
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-f",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "noise rollback and latency isolation candidate: official app vectors, official stream/IO paths, official UI resources, and only the AC/DC current-switch timing cluster patches",
    },
    "v401h-repair-g": {
        "fault_reset": False,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": None,
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": None,
        "command_retry_profile": None,
        "stream_state_clear_profile": None,
        "mode_state_clear_profile": None,
        "stream_busy_gate_profile": None,
        "current_switch_latency_profile": "cap-two-mode-range-clusters",
        "instant_switch_profile": "force-mode-call-immediate",
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-g",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "expanded latency isolation candidate: repair-f plus the earlier mode/range helper cluster that still used 0x3a98 state-2 guards",
    },
    "v401h-repair-h": {
        "fault_reset": False,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": None,
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": None,
        "command_retry_profile": None,
        "stream_state_clear_profile": None,
        "mode_state_clear_profile": None,
        "stream_busy_gate_profile": None,
        "current_switch_latency_profile": "cap-two-mode-range-clusters-plus-ammeter",
        "instant_switch_profile": "force-mode-call-immediate",
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-h",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "ammeter-mapped latency candidate: repair-g plus the AC/20A/mA function's own 0x3a98 state-2 guards",
    },
    "v401h-repair-i": {
        "fault_reset": False,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": None,
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": None,
        "command_retry_profile": None,
        "stream_state_clear_profile": None,
        "mode_state_clear_profile": None,
        "stream_busy_gate_profile": None,
        "current_switch_latency_profile": "cap-two-mode-range-clusters-plus-ammeter-fast-window",
        "instant_switch_profile": "force-mode-call-immediate",
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-i",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "clean ammeter latency candidate: repair-h plus a reduced ammeter sample acquisition window, with UI/system resources kept official",
    },
    "v401h-repair-i-ui-ms": {
        "fault_reset": False,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": None,
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": None,
        "command_retry_profile": None,
        "stream_state_clear_profile": None,
        "mode_state_clear_profile": None,
        "stream_busy_gate_profile": None,
        "current_switch_latency_profile": "cap-two-mode-range-clusters-plus-ammeter-fast-window",
        "instant_switch_profile": "force-mode-call-immediate",
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-i-ui-ms",
        "language_name_patch": True,
        "stage_text_resources": True,
        "sp_text_source": "safe-sp-layout",
        "boot_logo_delay": False,
        "description": "experimental UI overlay candidate: repair-i measurement bytes plus Melayu SP-slot name and safe SP-layout Malay text staging",
    },
    "v401h-repair-j": {
        "fault_reset": False,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": None,
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": None,
        "command_retry_profile": None,
        "stream_state_clear_profile": None,
        "mode_state_clear_profile": None,
        "stream_busy_gate_profile": None,
        "current_switch_latency_profile": "cap-acdc-switch-state-windows-240",
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-j",
        "language_name_patch": False,
        "stage_text_resources": False,
        "boot_logo_delay": False,
        "description": "single-change AC/DC switch-window candidate: official V4.0 plus the two AC/DC switch-state acquisition windows (600/360) lowered to the vendor's own 240; evidence in docs/v313-v316-v40-switching-comparison-2026-07-17.md",
    },
    "v401h-repair-j-ui-ms": {
        "fault_reset": False,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "stream_recovery_profile": None,
        "low_io_timeout_profile": None,
        "low_io_wrapper_profile": None,
        "command_retry_profile": None,
        "stream_state_clear_profile": None,
        "mode_state_clear_profile": None,
        "stream_busy_gate_profile": None,
        "current_switch_latency_profile": "cap-acdc-switch-state-windows-240",
        "instant_switch_profile": None,
        "stale_error_gate_profile": None,
        "version_patch_profile": "visible-repair-j-ui-ms",
        "language_name_patch": True,
        "stage_text_resources": True,
        "sp_text_source": "safe-sp-layout",
        "boot_logo_delay": False,
        "description": "combined candidate: repair-j measurement bytes (AC/DC switch windows 240) plus Melayu SP-slot name and safe SP-layout Malay text staging; measurement bytes identical to v401h-repair-j",
    },
}

ORIGINAL_FAULT_BLOCK = bytes.fromhex("fe e7 " * 10)

# Thumb code at 0x08017554:
#   ldr r0, [pc, #8]      ; r0 = 0xE000ED0C (SCB AIRCR)
#   ldr r1, [pc, #8]      ; r1 = 0x05FA0004 (VECTKEY | SYSRESETREQ)
#   str r1, [r0]
#   dsb sy
#   b .
#   .word 0xE000ED0C
#   .word 0x05FA0004
FAULT_RESET_STUB = (
    bytes.fromhex("02 48 02 49 01 60 bf f3 4f 8f fe e7")
    + (0xE000ED0C).to_bytes(4, "little")
    + (0x05FA0004).to_bytes(4, "little")
)

VERSION_PATCHES = {
    0x02CA0: b"MT100MM V4.0.1b\x00",
    0x02CB0: b"BT100MM V4.0.1b\x00",
}

VERSION_PATCHES_BY_PROFILE = {
    "visible-exp15": {
        0x02CA0: b"MT100MM V4.0.1c\x00",
        0x02CB0: b"BT100MM V4.0.1c\x00",
    },
    "visible-exp16": {
        0x02CA0: b"MT100MM V4.0.1d\x00",
        0x02CB0: b"BT100MM V4.0.1d\x00",
    },
    "visible-exp17": {
        0x02CA0: b"MT100MM V4.0.1e\x00",
        0x02CB0: b"BT100MM V4.0.1e\x00",
    },
    "visible-exp18": {
        0x02CA0: b"MT100MM V4.0.1f\x00",
        0x02CB0: b"BT100MM V4.0.1f\x00",
    },
    "visible-exp19": {
        0x02CA0: b"MT100MM V4.0.1g\x00",
        0x02CB0: b"BT100MM V4.0.1g\x00",
    },
    "visible-exp20": {
        0x02CA0: b"MT100MM V4.0.1h\x00",
        0x02CB0: b"BT100MM V4.0.1h\x00",
    },
    "visible-repair-c": {
        0x02CA0: b"MT100MM V4.0.1i\x00",
        0x02CB0: b"BT100MM V4.0.1i\x00",
    },
    "visible-repair-d": {
        0x02CA0: b"MT100MM V4.0.1j\x00",
        0x02CB0: b"BT100MM V4.0.1j\x00",
    },
    "visible-repair-e": {
        0x02CA0: b"MT100MM V4.0.1k\x00",
        0x02CB0: b"BT100MM V4.0.1k\x00",
    },
    "visible-repair-f": {
        0x02CA0: b"MT100MM V4.0.1l\x00",
        0x02CB0: b"BT100MM V4.0.1l\x00",
    },
    "visible-repair-g": {
        0x02CA0: b"MT100MM V4.0.1m\x00",
        0x02CB0: b"BT100MM V4.0.1m\x00",
    },
    "visible-repair-h": {
        0x02CA0: b"MT100MM V4.0.1n\x00",
        0x02CB0: b"BT100MM V4.0.1n\x00",
    },
    "visible-repair-i": {
        0x02CA0: b"MT100MM V4.0.1o\x00",
        0x02CB0: b"BT100MM V4.0.1o\x00",
    },
    "visible-repair-i-ui-ms": {
        0x02CA0: b"MT100MM V4.0.1p\x00",
        0x02CB0: b"BT100MM V4.0.1p\x00",
    },
    "visible-repair-j": {
        0x02CA0: b"MT100MM V4.0.1q\x00",
        0x02CB0: b"BT100MM V4.0.1q\x00",
    },
    "visible-repair-j-ui-ms": {
        0x02CA0: b"MT100MM V4.0.1r\x00",
        0x02CB0: b"BT100MM V4.0.1r\x00",
    },
}

LANGUAGE_NAME_PATCHES = {
    # Existing language-name table at 0x08035be4. The Spanish slot is reused
    # for Malay text/resources because no spare add-only slot is confirmed.
    # Keep the payload exactly seven bytes so the following entries do not move.
    0x25BF8: (
        b"Espa\xc3\xb1a",
        b"Melayu ",
        "rename existing Spanish language menu slot to Melayu without changing table size",
    ),
}

RUNTIME_ANTI_FREEZE_PATCHES = {
    # These are fail-stop/assertion paths outside the vector table. Normal
    # successful execution already returns before reaching these bytes.
    0x09CA0: (
        bytes.fromhex("ff e7"),
        "convert runtime fail-stop loop after integrity check into fall-through return",
    ),
    0x0C6C8: (
        bytes.fromhex("ff e7"),
        "convert UI/render fail-stop loop into fall-through return",
    ),
    0x2C4EA: (
        bytes.fromhex("70 47"),
        "return from semihosting/debug fail-stop instead of looping forever",
    ),
}

RUNTIME_ANTI_FREEZE_PATCHES_BY_PROFILE = {
    "full": RUNTIME_ANTI_FREEZE_PATCHES,
    "no-ui-render-fallthrough": {
        offset: patch
        for offset, patch in RUNTIME_ANTI_FREEZE_PATCHES.items()
        if offset != 0x0C6C8
    },
}

RELAY_SETTLE_PATCHES = {
    "exp1": {
        # Function 0x0801f0f2 is a GPIO/timing relay or range-selector candidate.
        # It is called repeatedly by 0x0801f19a when the active measurement path is
        # changed. The patch only extends waits that already exist in the official
        # firmware; it does not alter pin order or final pin states.
        0x0F10A: (
            bytes.fromhex("02 20"),
            bytes.fromhex("05 20"),
            "increase relay selector pre-switch settle wait from 2 to 5 ticks",
        ),
        0x0F146: (
            bytes.fromhex("03 20"),
            bytes.fromhex("08 20"),
            "increase relay selector bit-settle wait from 3 to 8 ticks",
        ),
        0x0F192: (
            bytes.fromhex("0a 20"),
            bytes.fromhex("32 20"),
            "increase final post-relay settle wait from 10 to 50 ticks",
        ),
    },
    "exp2": {
        # Stronger wait profile requested after hardware feedback that exp1 still
        # leaves blanking/instability after DC -> AC -> DC current switching.
        # This remains a timing-only patch at proven wait instructions.
        0x0F10A: (
            bytes.fromhex("02 20"),
            bytes.fromhex("08 20"),
            "force-stable: increase relay selector pre-switch settle wait from 2 to 8 ticks",
        ),
        0x0F146: (
            bytes.fromhex("03 20"),
            bytes.fromhex("0c 20"),
            "force-stable: increase relay selector bit-settle wait from 3 to 12 ticks",
        ),
        0x0F192: (
            bytes.fromhex("0a 20"),
            bytes.fromhex("64 20"),
            "force-stable: increase final post-relay settle wait from 10 to 100 ticks",
        ),
    },
}

MODE_SWITCH_PATCHES = {
    "v316-helper-wrapper": {
        # Helper 0x0801f0ac is called only from the mode-switch tail at
        # 0x0801f304/0x0801f310. V3.16 keeps a separate sub-mode check and
        # falls back to selector(1, flag) outside sub-mode 4. V4.0 always uses
        # this helper. The wrapper makes the helper perform selector(1, flag)
        # directly while preserving the call sites and official relay timing.
        0x0F0AC: (
            bytes.fromhex("10 b5 04 46 01 2c 08 d1 02 21 5e 48 1a f0 6d f9"),
            bytes.fromhex("00 b5 01 46 01 20 00 f0 1e f8 00 bd 00 bf 00 bf"),
            "v316-switch-exp3: replace V4 helper-only tail with selector(1, flag) wrapper for smoother DC/AC mode recovery",
        ),
    },
}

STREAM_RECOVERY_PATCHES = {
    "fail-fast-busy-retry": {
        # These branches are high-level retry loops around lower helpers that
        # already contain their own hardware-ready timeout. In the reported
        # failure, numeric reading and battery icon disappear together, which
        # points to the UI/status refresh path being blocked while these retry
        # loops keep waiting on a busy/valid flag. Replacing the retry branch
        # with NOP preserves the existing fall-through path that the official
        # code already uses when the same busy flag becomes zero.
        0x09570: (
            bytes.fromhex("f5 d1"),
            bytes.fromhex("00 bf"),
            "stream-recovery-shared: stop repeated 0xff stream-read retry after lower helper timeout; return failure to caller so UI/status refresh can resume",
        ),
        0x09706: (
            bytes.fromhex("ec d1"),
            bytes.fromhex("00 bf"),
            "stream-recovery-shared: stop repeated command-0x40 retry when lower command helper fails while busy flag remains asserted",
        ),
        0x09758: (
            bytes.fromhex("f5 d1"),
            bytes.fromhex("00 bf"),
            "stream-recovery-shared: stop repeated command-0xe9 retry when the lower command helper cannot clear the acquisition/status path",
        ),
        0x097BE: (
            bytes.fromhex("f6 d1"),
            bytes.fromhex("00 bf"),
            "stream-recovery-shared: stop repeated mode/status retry when the lower command helper cannot clear the acquisition/status path",
        ),
    },
    "fail-fast-error-route": {
        # Exp10 keeps the exp9 fail-fast intent, but improves the command-0x40
        # failure path. In exp9, the command-0x40 busy retry branch was changed
        # to NOP, which can fall through to the normal r6=0 path after the
        # command helper reports failure while the shared busy flag remains
        # nonzero. Here that one branch is redirected to the existing
        # error/clear sequence at 0x080197a2. That sequence sets r6=2, uses the
        # existing e9 clear command, reaches the same cleanup block, and with
        # the exp9 branch at 0x097be still NOPed cannot loop forever there.
        0x09570: (
            bytes.fromhex("f5 d1"),
            bytes.fromhex("00 bf"),
            "stream-recovery error-route: stop repeated 0xff stream-read retry after lower helper timeout; return failure to caller so UI/status refresh can resume",
        ),
        0x09706: (
            bytes.fromhex("ec d1"),
            bytes.fromhex("4c d1"),
            "stream-recovery error-route: route command-0x40 failure with busy flag set to existing error/clear path instead of treating it as normal fall-through",
        ),
        0x09758: (
            bytes.fromhex("f5 d1"),
            bytes.fromhex("00 bf"),
            "stream-recovery error-route: stop repeated command-0xe9 retry when the lower command helper cannot clear the acquisition/status path",
        ),
        0x097BE: (
            bytes.fromhex("f6 d1"),
            bytes.fromhex("00 bf"),
            "stream-recovery error-route: stop repeated mode/status retry when the lower command helper cannot clear the acquisition/status path",
        ),
    },
}

LOW_IO_TIMEOUT_PATCHES = {
    "half-timeout": {
        # Function 0x08016a06 reads one byte through the external measurement
        # communication path. It already has bounded hardware-ready waits, but
        # the bound is 0x2710 iterations twice per byte. When a spike/overload
        # leaves the ready flag stuck, these waits multiply across repeated
        # reads and can starve UI/status refresh. Keep the same fail path and
        # only reduce the wait from 0x2710 to 0x1388.
        0x06A1C: (
            bytes.fromhex("42 f2 10 70"),
            bytes.fromhex("41 f2 88 30"),
            "stream-recovery-exp7: reduce first lower byte-IO hardware-ready timeout from 0x2710 to 0x1388 for faster fail/recover",
        ),
        0x06A3E: (
            bytes.fromhex("42 f2 10 70"),
            bytes.fromhex("41 f2 88 30"),
            "stream-recovery-exp7: reduce second lower byte-IO hardware-ready timeout from 0x2710 to 0x1388 for faster fail/recover",
        ),
    },
    "tight-timeout": {
        # Fine-tune after exp7: keep the same two bounded wait locations and
        # failure path, but lower the wait to 0x0fa0. This is still a
        # recovery/latency patch, not an ADC/math/filter patch.
        0x06A1C: (
            bytes.fromhex("42 f2 10 70"),
            bytes.fromhex("40 f6 a0 70"),
            "stream-recovery tight-timeout: reduce first lower byte-IO hardware-ready timeout from 0x2710 to 0x0fa0 for lower recovery latency",
        ),
        0x06A3E: (
            bytes.fromhex("42 f2 10 70"),
            bytes.fromhex("40 f6 a0 70"),
            "stream-recovery tight-timeout: reduce second lower byte-IO hardware-ready timeout from 0x2710 to 0x0fa0 for lower recovery latency",
        ),
    },
}

COMMAND_RETRY_PATCHES = {
    "balanced-0x60": {
        # Function 0x08019608 polls command status after sending command 0x40
        # or 0x48. The original bounded counters are high enough to stretch
        # worst-case latency after overload or a stuck status bit. Keep the same
        # status path and fallback count, but clamp the two long command waits
        # to 0x60.
        0x0967C: (
            bytes.fromhex("95 27"),
            bytes.fromhex("60 27"),
            "stream-recovery balanced clamp: reduce command-0x40 bounded status retry count from 0x95 to 0x60",
        ),
        0x09682: (
            bytes.fromhex("87 27"),
            bytes.fromhex("60 27"),
            "stream-recovery balanced clamp: reduce command-0x48 bounded status retry count from 0x87 to 0x60",
        ),
    },
}

STREAM_STATE_CLEAR_PATCHES = {
    "clear-error-and-stale-busy": {
        # Function 0x080196b2 writes a stream/status result and, on nonzero
        # error result, clears bit 0 from RAM flag 0x2000022c. Field evidence
        # shows numeric readings and the battery icon can disappear together
        # after spike/overload or AC/DC switching. Static tracing shows bit 1
        # of the same flag is an early-return/stale-busy gate. Clearing bits
        # 0 and 1 on the existing error path releases stale busy state without
        # clearing the other observed protection/status bits.
        0x097E6: (
            bytes.fromhex("20 f0 01 00"),
            bytes.fromhex("20 f0 03 00"),
            "stream-recovery state-clear: on existing stream error cleanup, clear flag bits 0 and 1 from 0x2000022c instead of only bit 0 so stale busy/status cannot persist after timeout/spike",
        ),
    },
}

MODE_STATE_CLEAR_ENTRY_OFFSET = 0x0F19A
MODE_STATE_CLEAR_WRAPPER_OFFSET = 0x2D606
MODE_STATE_CLEAR_WRAPPER_GUARD_SIZE = 30
MODE_STATE_CLEAR_FLAG_ADDRESS = 0x2000022C
MODE_STATE_CLEAR_RETURN_ADDRESS = LOAD_BASE + MODE_STATE_CLEAR_ENTRY_OFFSET + 4


def build_mode_state_clear_wrapper() -> bytes:
    """Preserve the original mode/range prologue, clear stale bits, then return."""
    return (
        bytes.fromhex(
            "10 b5"  # original push {r4, lr}
            "04 46"  # original mov r4, r0
            "04 49"  # ldr r1, =0x2000022c
            "0a 78"  # ldrb r2, [r1]
            "22 f0 03 02"  # bic r2, r2, #3
            "0a 70"  # strb r2, [r1]
            "02 4b"  # ldr r3, =return_address|1
            "18 47"  # bx r3
            "00 bf"
            "00 bf"
        )
        + MODE_STATE_CLEAR_FLAG_ADDRESS.to_bytes(4, "little")
        + (MODE_STATE_CLEAR_RETURN_ADDRESS | 1).to_bytes(4, "little")
    )


MODE_STATE_CLEAR_PATCHES = {
    "mode-range-clear-stale-busy": {
        MODE_STATE_CLEAR_ENTRY_OFFSET: (
            bytes.fromhex("10 b5 04 46"),
            lambda: encode_thumb_b_w(
                LOAD_BASE + MODE_STATE_CLEAR_ENTRY_OFFSET,
                LOAD_BASE + MODE_STATE_CLEAR_WRAPPER_OFFSET,
            ),
            "stream-recovery-exp13: route mode/range entry through stale stream-state clear wrapper before relay switching",
        ),
        MODE_STATE_CLEAR_WRAPPER_OFFSET: (
            b"\x00" * MODE_STATE_CLEAR_WRAPPER_GUARD_SIZE,
            build_mode_state_clear_wrapper,
            "stream-recovery-exp13: preserve original mode/range prologue, clear bits 0 and 1 of 0x2000022c, then continue original function",
        ),
    },
}

STREAM_BUSY_GATE_PATCHES = {
    "force-stream-transaction": {
        # Function 0x080196b2 checks bit 1 of 0x2000022c near entry and, when
        # set, returns before starting a fresh measurement transaction. Field
        # evidence after exp13 shows AC->DC in ammeter can still wait around
        # 30 seconds even though the mode/range entry clears the flag. That
        # means the stale-busy gate can be reasserted after the entry wrapper
        # or before the next stream call. This patch changes the conditional
        # early-return gate into an unconditional branch to the normal
        # transaction body. It does not alter the lower byte-IO timeout wrapper
        # or the existing error cleanup path, so a genuinely stuck helper must
        # still fail through bounded recovery instead of spinning forever.
        0x096BE: (
            bytes.fromhex("10 b1"),
            bytes.fromhex("02 e0"),
            "stream-recovery-exp14: force fresh stream transaction instead of returning early on stale busy bit 1 at 0x2000022c",
        ),
    },
}

CURRENT_SWITCH_LATENCY_PATCHES = {
    "cap-long-switch-gate-0x0640": {
        # Two nearby current/meter transition gates compare against 0x3e80.
        # The user's measured AC->DC ammeter blank time is about 30 seconds,
        # which matches this budget when the device tick is near 2ms. Use the
        # existing 0x0640 compare encoding already present in the same timing
        # cluster to cap the long wait without removing the guard entirely.
        0x1585E: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "stream-recovery-exp14: cap long current/meter switch gate from 0x3e80 to 0x0640 to reduce AC-to-DC recovery latency",
        ),
        0x15888: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "stream-recovery-exp14: cap second long current/meter switch gate from 0x3e80 to 0x0640 to reduce repeated blanking after mode return",
        ),
    },
    "cap-long-switch-gate-0x0640-plus-state2": {
        # Repair-a did not improve the field symptom. A byte audit of the same
        # timing cluster found two later state-2 guards still loading 0x3a98.
        # Lower them to 0x05dc, a vendor-used settle budget in the same
        # function, while retaining the original exp14 0x3e80 -> 0x0640 caps.
        0x1585E: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "v401h-repair-b: cap first long current/meter switch compare from 0x3e80 to 0x0640",
        ),
        0x15888: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "v401h-repair-b: cap second long current/meter switch compare from 0x3e80 to 0x0640",
        ),
        0x15934: (
            bytes.fromhex("43 f6 98 21"),
            bytes.fromhex("40 f2 dc 51"),
            "v401h-repair-b: lower remaining state-2 current/meter switch guard from 0x3a98 to vendor-adjacent 0x05dc",
        ),
        0x1595C: (
            bytes.fromhex("43 f6 98 21"),
            bytes.fromhex("40 f2 dc 51"),
            "v401h-repair-b: lower second remaining state-2 current/meter switch guard from 0x3a98 to vendor-adjacent 0x05dc",
        ),
    },
    "cap-two-mode-range-clusters": {
        # Repair-f proved the cleanest rollback profile, but a full scan found
        # another mode/range helper cluster at 0x08024b0e and 0x08024b36 that
        # still calls 0x0801f19a after two state-2 0x3a98 guards. Lower only
        # those guards to the same vendor-adjacent 0x05dc budget. This keeps
        # stream/IO, ADC math, relay settle, UI, and resource behavior official.
        0x14B0E: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-g: lower earlier mode/range state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x14B36: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-g: lower second earlier mode/range state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1585E: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "v401h-repair-g: cap first long current/meter switch compare from 0x3e80 to 0x0640",
        ),
        0x15888: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "v401h-repair-g: cap second long current/meter switch compare from 0x3e80 to 0x0640",
        ),
        0x15934: (
            bytes.fromhex("43 f6 98 21"),
            bytes.fromhex("40 f2 dc 51"),
            "v401h-repair-g: lower remaining current/meter state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1595C: (
            bytes.fromhex("43 f6 98 21"),
            bytes.fromhex("40 f2 dc 51"),
            "v401h-repair-g: lower second remaining current/meter state-2 guard from 0x3a98 to 0x05dc",
        ),
    },
    "cap-two-mode-range-clusters-plus-ammeter": {
        # Repair-g still did not touch the function now mapped by UI text to
        # AC / 20A(Yellow) / mA(Green). That function starts near 0x0802d194
        # and loads two 0x3a98 state-2 guard budgets before drawing the
        # ammeter AC/range labels and calling mode/range helper 0x0801f19a.
        # Lower only those two ammeter-local guard budgets in addition to the
        # cleaner Repair-G timing patches.
        0x14B0E: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-h: lower earlier mode/range state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x14B36: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-h: lower second earlier mode/range state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1585E: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "v401h-repair-h: cap first long current/meter switch compare from 0x3e80 to 0x0640",
        ),
        0x15888: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "v401h-repair-h: cap second long current/meter switch compare from 0x3e80 to 0x0640",
        ),
        0x15934: (
            bytes.fromhex("43 f6 98 21"),
            bytes.fromhex("40 f2 dc 51"),
            "v401h-repair-h: lower remaining current/meter state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1595C: (
            bytes.fromhex("43 f6 98 21"),
            bytes.fromhex("40 f2 dc 51"),
            "v401h-repair-h: lower second remaining current/meter state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1D1A4: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-h: lower ammeter AC/20A/mA state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1D1C0: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-h: lower second ammeter AC/20A/mA state-2 guard from 0x3a98 to 0x05dc",
        ),
    },
    "cap-two-mode-range-clusters-plus-ammeter-fast-window": {
        # Repair-i keeps Repair-H's clean latency isolation and adds one more
        # ammeter-local patch. In the same AC/20A/mA function, V4.0 stores
        # 0xf0 (240) as the sample acquisition window before the numeric
        # update loop. A 240-sample wait can match the reported ~30 second
        # AC->DC blank when the effective sample cadence collapses near 8/s.
        # Reduce only this ammeter window to 0x40 (64) so the device still
        # averages multiple samples, but the post-switch blank should be much
        # shorter than the official V4.0 path. This is deliberately isolated
        # from stream/IO wrappers, relay order, ADC scaling constants, and UI
        # resources because those earlier experiments either did not help or
        # made noise/rendering worse.
        0x14B0E: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-i: lower earlier mode/range state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x14B36: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-i: lower second earlier mode/range state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1585E: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "v401h-repair-i: cap first long current/meter switch compare from 0x3e80 to 0x0640",
        ),
        0x15888: (
            bytes.fromhex("b0 f5 7a 5f"),
            bytes.fromhex("b0 f5 c8 6f"),
            "v401h-repair-i: cap second long current/meter switch compare from 0x3e80 to 0x0640",
        ),
        0x15934: (
            bytes.fromhex("43 f6 98 21"),
            bytes.fromhex("40 f2 dc 51"),
            "v401h-repair-i: lower remaining current/meter state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1595C: (
            bytes.fromhex("43 f6 98 21"),
            bytes.fromhex("40 f2 dc 51"),
            "v401h-repair-i: lower second remaining current/meter state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1D1A4: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-i: lower ammeter AC/20A/mA state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1D1C0: (
            bytes.fromhex("43 f6 98 20"),
            bytes.fromhex("40 f2 dc 50"),
            "v401h-repair-i: lower second ammeter AC/20A/mA state-2 guard from 0x3a98 to 0x05dc",
        ),
        0x1D1DA: (
            bytes.fromhex("f0 20"),
            bytes.fromhex("40 20"),
            "v401h-repair-i: reduce ammeter AC/20A/mA acquisition window from 240 samples to 64 samples to lower AC->DC blank latency",
        ),
    },
    "cap-acdc-switch-state-windows-240": {
        # Repair-j: single-change candidate from the three-way vendor
        # comparison (docs/v313-v316-v40-switching-comparison-2026-07-17.md).
        # V3.13/V3.16 share V4.0's 0x3a98 guards and switch smoothly, so the
        # repair-a..i guard caps were never the cause. In V4.0 the ammeter
        # AC<->DC switch-state handler (state 0x2d) overwrites the acquisition
        # window with 600 (0x258) or 360 (0x168) polled samples on every
        # switch; 600 samples at the collapsed poll cadence matches the
        # reported ~30 s blank. Lower both to the vendor's own normal-update
        # window of 240 (0xf0) samples. Encoding: mov.w r0,#imm (no flags)
        # -> movw r0,#0xf0 (no flags), so the following `str r0,[sp,#0x10]`
        # and flag state are unaffected.
        0x1DF0C: (
            bytes.fromhex("4f f4 16 70"),
            bytes.fromhex("40 f2 f0 00"),
            "v401h-repair-j: lower AC->DC switch-state acquisition window from 600 samples (0x258) to vendor's 240 (0xf0)",
        ),
        0x1DF40: (
            bytes.fromhex("4f f4 b4 70"),
            bytes.fromhex("40 f2 f0 00"),
            "v401h-repair-j: lower DC->AC switch-state acquisition window from 360 samples (0x168) to vendor's 240 (0xf0)",
        ),
    },
}

INSTANT_SWITCH_PATCHES = {
    "force-mode-call-immediate": {
        # The exp14 compare cap proved insufficient in field testing. These
        # four guarded branches are the delay gates immediately before the
        # mode/range calls in the same switch cluster. Replacing each branch
        # with NOP preserves the surrounding direction/state checks but lets
        # the firmware call mode_range immediately once a switch condition is
        # detected, instead of waiting for an elapsed-time threshold.
        0x15812: (
            bytes.fromhex("05 d9"),
            bytes.fromhex("00 bf"),
            "stream-recovery-exp15: do not delay first immediate mode/range call after switch condition",
        ),
        0x15838: (
            bytes.fromhex("34 d9"),
            bytes.fromhex("00 bf"),
            "stream-recovery-exp15: do not delay second immediate mode/range call after switch condition",
        ),
        0x15862: (
            bytes.fromhex("06 d9"),
            bytes.fromhex("00 bf"),
            "stream-recovery-exp15: do not delay first return-to-mode call after AC/DC switch condition",
        ),
        0x1588C: (
            bytes.fromhex("05 d9"),
            bytes.fromhex("00 bf"),
            "stream-recovery-exp15: do not delay second return-to-mode call after AC/DC switch condition",
        ),
    },
}

STALE_ERROR_GATE_PATCHES = {
    "ignore-bit0-error-gates": {
        # Three stream transfer helpers return immediately with error code 3
        # when bit 0 of 0x2000022c is set. Exp13/exp14 clear bit 0 on entry
        # and error cleanup, but the field result shows the blank still
        # survives. These patches convert the "continue only if zero" checks
        # into unconditional branches to the normal helper body. This is an
        # aggressive stale-state recovery patch; real overload protection must
        # still be validated on dummy loads.
        0x09818: (
            bytes.fromhex("08 b1"),
            bytes.fromhex("01 e0"),
            "stream-recovery-exp15: bypass stale bit0 error gate in first stream transfer helper",
        ),
        0x098B4: (
            bytes.fromhex("08 b1"),
            bytes.fromhex("01 e0"),
            "stream-recovery-exp15: bypass stale bit0 error gate in second stream transfer helper",
        ),
        0x09950: (
            bytes.fromhex("18 b1"),
            bytes.fromhex("03 e0"),
            "stream-recovery-exp15: bypass stale bit0 error gate in parsed stream transfer helper",
        ),
    },
}

LOW_IO_WRAPPER_PATCHES = {
    "bounded-fail-0xfa0": {
        # Exp11 replaces the low byte-IO helper entry with a local branch to a
        # bounded wrapper placed over adjacent setup code that has no direct or
        # literal callers in this image. The wrapper keeps the same SPI1 HAL
        # calls and the exp10 0x0fa0 wait budget, but returns 0xff if either
        # ready flag never appears. That makes timeout visible to the existing
        # high-level stream recovery instead of continuing with a stale read.
        0x06A06: (
            bytes.fromhex("70 b5 05 46"),
            bytes.fromhex("00 f0 23 b8"),
            "stream-recovery-exp11: branch low byte-IO helper to bounded failure-return wrapper",
        ),
        0x06A50: (
            bytes.fromhex(
                "00 b5 85 b0 23 48 23 f0 fd fe 01 21 88 03 23 f0 ac f8 "
                "00 20 ad f8 00 00 4f f4 82 70 ad f8 02 00 00 20 ad f8 "
                "04 00 02 20 ad f8 06 00 01 20 ad f8 08 00 40 02 ad f8 "
                "0a 00 08 20 ad f8 0c 00 00 20 ad f8 0e 00 07 20 ad f8 "
                "10 00 69 46 11 48 23 f0"
            ),
            bytes.fromhex(
                "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
                "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
                "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
                "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
                "70 bd 00 bf 00 30 01 40"
            ),
            "stream-recovery-exp11: bounded low byte-IO wrapper returns 0xff on ready-timeout and preserves SPI1 read/write calls",
        ),
    },
}

BOOT_LOGO_DELAY_CALL_OFFSET = 0x045B2
BOOT_LOGO_DELAY_STUB_OFFSET = 0x2D5C0
BOOT_LOGO_ORIGINAL_LOAD = 0x08015EEE
BOOT_LOGO_DELAY_FUNCTION = 0x08017AC2
BOOT_LOGO_DELAY_TICKS = 0xC8
BOOT_LOGO_STUB_GUARD_SIZE = 32


def encode_thumb_bl(source_address: int, target_address: int) -> bytes:
    """Encode a Thumb-2 BL. Source is the address of the BL halfword pair."""
    offset = target_address - (source_address + 4)
    if offset % 2:
        raise ValueError("Thumb BL target must be halfword aligned")
    imm = offset >> 1
    if not (-(1 << 23) <= imm < (1 << 23)):
        raise ValueError("Thumb BL target is out of range")
    imm &= (1 << 24) - 1
    sign = (imm >> 23) & 1
    i1 = (imm >> 22) & 1
    i2 = (imm >> 21) & 1
    imm10 = (imm >> 11) & 0x03FF
    imm11 = imm & 0x07FF
    j1 = (~(i1 ^ sign)) & 1
    j2 = (~(i2 ^ sign)) & 1
    first = 0xF000 | (sign << 10) | imm10
    second = 0xF800 | (j1 << 13) | (j2 << 11) | imm11
    return first.to_bytes(2, "little") + second.to_bytes(2, "little")


def encode_thumb_b_w(source_address: int, target_address: int) -> bytes:
    """Encode a Thumb-2 unconditional B.W. Source is the first halfword."""
    offset = target_address - (source_address + 4)
    if offset % 2:
        raise ValueError("Thumb B.W target must be halfword aligned")
    imm = offset >> 1
    if not (-(1 << 23) <= imm < (1 << 23)):
        raise ValueError("Thumb B.W target is out of range")
    imm &= (1 << 24) - 1
    sign = (imm >> 23) & 1
    i1 = (imm >> 22) & 1
    i2 = (imm >> 21) & 1
    imm10 = (imm >> 11) & 0x03FF
    imm11 = imm & 0x07FF
    j1 = (~(i1 ^ sign)) & 1
    j2 = (~(i2 ^ sign)) & 1
    first = 0xF000 | (sign << 10) | imm10
    second = 0x9000 | (j1 << 13) | (j2 << 11) | imm11
    return first.to_bytes(2, "little") + second.to_bytes(2, "little")


def build_boot_logo_delay_stub() -> bytes:
    stub_address = LOAD_BASE + BOOT_LOGO_DELAY_STUB_OFFSET
    original_call = encode_thumb_bl(stub_address + 2, BOOT_LOGO_ORIGINAL_LOAD)
    delay_call = encode_thumb_bl(stub_address + 8, BOOT_LOGO_DELAY_FUNCTION)
    return (
        bytes.fromhex("10 b5")
        + original_call
        + bytes([BOOT_LOGO_DELAY_TICKS, 0x20])
        + delay_call
        + bytes.fromhex("10 bd")
    )


@dataclass(frozen=True)
class PatchRecord:
    offset: int
    before: bytes
    after: bytes
    reason: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def u32_at(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def patch_bytes(image: bytearray, offset: int, after: bytes, reason: str) -> PatchRecord:
    before = bytes(image[offset : offset + len(after)])
    image[offset : offset + len(after)] = after
    return PatchRecord(offset, before, after, reason)


def find_self_loop_vectors(data: bytes) -> list[int]:
    vector_offsets: list[int] = []
    for index in range(1, min(VECTOR_WORDS, len(data) // 4)):
        entry_offset = index * 4
        value = u32_at(data, entry_offset)
        target = (value & ~1) - LOAD_BASE
        if not (0 <= target + 2 <= len(data)):
            continue
        if data[target : target + 2] != b"\xfe\xe7":
            continue
        if FAULT_BLOCK_OFFSET <= target < FAULT_BLOCK_OFFSET + FAULT_BLOCK_SIZE:
            vector_offsets.append(entry_offset)
    return vector_offsets


def write_report(
    records: list[PatchRecord],
    source_data: bytes,
    output_data: bytes,
    profile: str,
    fault_reset: bool,
    runtime_patches: bool,
    runtime_patch_profile: str | None,
    relay_settle_profile: str | None,
    mode_switch_profile: str | None,
    stream_recovery_profile: str | None,
    low_io_timeout_profile: str | None,
    low_io_wrapper_profile: str | None,
    command_retry_profile: str | None,
    stream_state_clear_profile: str | None,
    mode_state_clear_profile: str | None,
    stream_busy_gate_profile: str | None,
    current_switch_latency_profile: str | None,
    instant_switch_profile: str | None,
    stale_error_gate_profile: str | None,
    version_patch_profile: str | None,
    boot_logo_delay: bool,
    vector_count: int,
) -> None:
    fault_scope = (
        "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub."
        if fault_reset
        else "- Flashable profile keeps fault/default handlers unchanged."
    )
    if not runtime_patches:
        runtime_scope = "- Flashable profile keeps runtime fail-stop loops unchanged."
    elif runtime_patch_profile == "no-ui-render-fallthrough":
        runtime_scope = (
            "- Runtime anti-freeze is limited to non-UI fail-stop loops. "
            "The UI/render loop at `0x0801c6c8` is kept official to avoid "
            "fall-through drawing artifacts."
        )
    else:
        runtime_scope = "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever."
    if relay_settle_profile == "exp1":
        relay_scope = "- Relay/range selector waits in function `0x0801f0f2` are extended to `5/8/50` ticks."
    elif relay_settle_profile == "exp2":
        relay_scope = "- Relay/range selector waits in function `0x0801f0f2` are extended to `8/12/100` ticks for stronger AC/DC switching recovery."
    else:
        relay_scope = "- Relay/range selector timing is kept unchanged."
    if mode_switch_profile == "v316-helper-wrapper":
        mode_scope = (
            "- Mode-switch helper `0x0801f0ac` is wrapped to call "
            "`selector(1, flag)` directly, matching the smoother V3.16 "
            "non-sub-mode-4 path while leaving call sites unchanged."
        )
    else:
        mode_scope = "- Mode-switch helper behavior is kept unchanged."
    if stream_recovery_profile == "fail-fast-busy-retry":
        stream_scope = (
            "- High-level measurement stream/status retry loops are changed to "
            "fail fast after the lower helper has already timed out, allowing "
            "normal UI/status refresh to resume instead of waiting indefinitely."
        )
    elif stream_recovery_profile == "fail-fast-error-route":
        stream_scope = (
            "- High-level measurement stream/status retry loops use fail-fast "
            "recovery, and command `0x40` busy failure routes into the existing "
            "error/clear sequence instead of normal fall-through."
        )
    else:
        stream_scope = "- High-level measurement stream/status retry loops are kept unchanged."
    if low_io_wrapper_profile == "bounded-fail-0xfa0":
        low_io_scope = (
            "- Low byte-IO helper `0x08016a06` is routed to a bounded wrapper "
            "that keeps a `0x0fa0` ready-wait budget and returns `0xff` if "
            "either ready flag never appears. This exposes timeout to the "
            "existing stream recovery instead of continuing with a stale read."
        )
    elif low_io_timeout_profile == "half-timeout":
        low_io_scope = (
            "- Lower byte-IO hardware-ready timeout in `0x08016a06` is reduced "
            "from `0x2710` to `0x1388` at both guarded wait points, preserving "
            "the existing timeout/failure path but reducing worst-case latency."
        )
    elif low_io_timeout_profile == "tight-timeout":
        low_io_scope = (
            "- Lower byte-IO hardware-ready timeout in `0x08016a06` is reduced "
            "from `0x2710` to `0x0fa0` at both guarded wait points, preserving "
            "the existing timeout/failure path while lowering recovery latency "
            "further than exp7."
        )
    else:
        low_io_scope = "- Lower byte-IO hardware-ready timeout is kept unchanged."
    if command_retry_profile == "balanced-0x60":
        command_retry_scope = (
            "- Command helper `0x08019608` keeps the same status polling path "
            "but reduces command `0x40` and `0x48` retry counts to `0x60` for "
            "lower worst-case status latency."
        )
    else:
        command_retry_scope = "- Command helper retry counters are kept unchanged."
    if stream_state_clear_profile == "clear-error-and-stale-busy":
        state_clear_scope = (
            "- Existing stream error cleanup now clears bits `0` and `1` from "
            "flag `0x2000022c`, releasing stale busy/status after timeout, "
            "spike, overload, or failed mode transition while leaving the "
            "other observed protection/status bits untouched."
        )
    else:
        state_clear_scope = "- Stream error-state cleanup is kept unchanged."
    if mode_state_clear_profile == "mode-range-clear-stale-busy":
        mode_state_scope = (
            "- Mode/range function `0x0801f19a` now enters through a guarded "
            "wrapper that preserves its original prologue, clears stale bits "
            "`0` and `1` from flag `0x2000022c`, then continues the original "
            "relay/range switching code. This targets blank/freeze after "
            "DC/AC/DC switching without changing relay GPIO order."
        )
    else:
        mode_state_scope = "- Mode/range entry state is kept unchanged."
    if stream_busy_gate_profile == "force-stream-transaction":
        stream_busy_scope = (
            "- Stream function `0x080196b2` no longer returns early only "
            "because stale busy bit `1` in `0x2000022c` is set. It branches "
            "to the normal transaction body so AC->DC recovery can request a "
            "fresh sample instead of waiting for the stale gate to expire."
        )
    else:
        stream_busy_scope = "- Stream busy early-return gate is kept unchanged."
    if current_switch_latency_profile == "cap-long-switch-gate-0x0640":
        current_latency_scope = (
            "- Two long meter/current transition guards that compared against "
            "`0x3e80` are capped to `0x0640`. This targets the reported "
            "approximately 30-second AC->DC ammeter blank while keeping a "
            "bounded settle guard in place."
        )
    elif current_switch_latency_profile == "cap-long-switch-gate-0x0640-plus-state2":
        current_latency_scope = (
            "- Four meter/current transition guards in the same timing cluster "
            "are capped: two `0x3e80` compares are changed to `0x0640`, and "
            "two remaining state-2 `0x3a98` guards are changed to the "
            "vendor-adjacent `0x05dc` settle budget."
        )
    elif current_switch_latency_profile == "cap-two-mode-range-clusters":
        current_latency_scope = (
            "- Six mode/range transition guards are capped across two helper "
            "clusters: the original four current/meter guards plus two earlier "
            "state-2 `0x3a98` guards that also call `0x0801f19a`. All are "
            "lowered to vendor-adjacent bounded settle values without touching "
            "stream/IO or ADC math."
        )
    elif current_switch_latency_profile == "cap-two-mode-range-clusters-plus-ammeter":
        current_latency_scope = (
            "- Eight transition guards are capped: Repair-G's six mode/range "
            "guards plus two `0x3a98` state-2 guards in the function mapped by "
            "UI text to `AC`, `20A(Yellow)`, and `mA(Green)`. This directly "
            "targets the reported ammeter green AC -> DC latency while keeping "
            "stream/IO, ADC math, relay settle, and UI resources official."
        )
    elif current_switch_latency_profile == "cap-two-mode-range-clusters-plus-ammeter-fast-window":
        current_latency_scope = (
            "- Eight transition guards are capped as in Repair-H, and the "
            "same AC/20A/mA ammeter function's acquisition window is reduced "
            "from `0xf0`/240 samples to `0x40`/64 samples. This targets the "
            "reported long AC -> DC blank after current-mode switching while "
            "keeping stream/IO wrappers, relay order, ADC scaling constants, "
            "and UI resources official."
        )
    elif current_switch_latency_profile == "cap-acdc-switch-state-windows-240":
        current_latency_scope = (
            "- Single-change candidate: the ammeter AC<->DC switch-state "
            "handler's acquisition windows (600/360 polled samples at "
            "`0x1df0c`/`0x1df40`) are lowered to the vendor's own 240-sample "
            "normal-update window. Three-way vendor comparison showed V3.13 "
            "and V3.16 share V4.0's 0x3a98 guards and switch smoothly, so "
            "the repair-a..i guard caps are absent here; everything else in "
            "the firmware is official V4.0."
        )
    else:
        current_latency_scope = "- Long meter/current transition guards are kept unchanged."
    if instant_switch_profile == "force-mode-call-immediate":
        instant_switch_scope = (
            "- Four elapsed-time skip branches immediately before mode/range "
            "calls are replaced with NOPs. Direction/state checks remain, but "
            "the mode/range call is no longer delayed once the switch "
            "condition is detected."
        )
    else:
        instant_switch_scope = "- Immediate mode/range switch gates are kept unchanged."
    if stale_error_gate_profile == "ignore-bit0-error-gates":
        stale_error_scope = (
            "- Three stream transfer helpers bypass stale bit `0` early error "
            "returns and continue into the normal helper body. This is an "
            "aggressive recovery test for the no-improvement exp14 result."
        )
    else:
        stale_error_scope = "- Stream transfer helper bit0 error gates are kept unchanged."
    if version_patch_profile == "visible-exp15":
        version_scope = "- Version strings are marked `V4.0.1c` as a visible exp15 flash marker."
    elif version_patch_profile == "visible-exp16":
        version_scope = "- Version strings are marked `V4.0.1d` as a visible exp16 UI-safe flash marker."
    elif version_patch_profile == "visible-exp17":
        version_scope = "- Version strings are marked `V4.0.1e` as a visible exp17 clean resource-restore flash marker."
    elif version_patch_profile == "visible-exp18":
        version_scope = "- Version strings are marked `V4.0.1f` as a visible exp18 resource-complete stability flash marker."
    elif version_patch_profile == "visible-exp19":
        version_scope = "- Version strings are marked `V4.0.1g` as a visible exp19 UI-restored stability flash marker."
    elif version_patch_profile == "visible-exp20":
        version_scope = "- Version strings are marked `V4.0.1h` as a visible exp20 safe-Malay-SP flash marker."
    elif version_patch_profile == "visible-repair-c":
        version_scope = "- Version strings are marked `V4.0.1i` as a visible repair-c measurement flash marker."
    elif version_patch_profile == "visible-repair-d":
        version_scope = "- Version strings are marked `V4.0.1j` as a visible repair-d UI-safe latency flash marker."
    elif version_patch_profile == "visible-repair-e":
        version_scope = "- Version strings are marked `V4.0.1k` as a visible repair-e clean-UI measurement flash marker."
    elif version_patch_profile == "visible-repair-f":
        version_scope = "- Version strings are marked `V4.0.1l` as a visible repair-f noise-rollback latency-isolation flash marker."
    elif version_patch_profile == "visible-repair-g":
        version_scope = "- Version strings are marked `V4.0.1m` as a visible repair-g expanded latency-isolation flash marker."
    elif version_patch_profile == "visible-repair-h":
        version_scope = "- Version strings are marked `V4.0.1n` as a visible repair-h ammeter-mapped latency flash marker."
    elif version_patch_profile == "visible-repair-i":
        version_scope = "- Version strings are marked `V4.0.1o` as a visible repair-i clean ammeter-latency flash marker."
    elif version_patch_profile == "visible-repair-i-ui-ms":
        version_scope = "- Version strings are marked `V4.0.1p` as a visible repair-i UI/Melayu overlay flash marker."
    elif version_patch_profile == "visible-repair-j":
        version_scope = "- Version strings are marked `V4.0.1q` as a visible repair-j AC/DC switch-window flash marker."
    else:
        version_scope = "- Version strings are marked `V4.0.1b`."
    boot_scope = (
        "- Boot-logo resource load is routed through a guarded wrapper that adds a short stabilization delay after `LOGO-1.bmp` is loaded."
        if boot_logo_delay
        else "- Boot-logo resource load timing is kept unchanged."
    )
    stage_text_resources = bool(PROFILES[profile].get("stage_text_resources", True))
    if not stage_text_resources:
        ms_resource_scope = "- Malay text/resource staging is disabled for this repair profile so official UI resources can be preserved."
        sp_resource_scope = "- The existing language resources are not staged or replaced by this patcher profile."
        language_name_scope = "- The Spanish language-name string is kept unchanged for this repair profile."
    else:
        ms_resource_scope = "- Bahasa Melayu resource is added to the candidate folder as `system/TEXT_MS.DAT`."
        sp_resource_scope = (
            "- The existing Spanish language slot is kept official in this profile; Malay remains staged only until the slot-size/UI smear issue is solved."
            if not PROFILES[profile].get("language_name_patch", True)
            else "- The existing Spanish `TEXT_SP.DAT` slot is replaced with the same Malay resource for device-side language selection."
        )
        language_name_scope = (
            "- The Spanish language-name string is kept unchanged for this UI-safe profile."
            if not PROFILES[profile].get("language_name_patch", True)
            else "- The existing Spanish language-name string is renamed to `Melayu` in place, with byte length preserved."
        )
    lines = [
        "# DM303 V4.0.1 beta patch report",
        "",
        "Status: candidate firmware only. Bench validation is still required before flashing.",
        "",
        f"Profile: `{profile}` - {PROFILES[profile]['description']}.",
        "",
        "## Safety scope",
        "",
        "- Source firmware is not modified in place.",
        "- Output binary size is unchanged.",
        "- Bootloader/updater code and SD update procedure are not patched.",
        fault_scope,
        runtime_scope,
        relay_scope,
        mode_scope,
        stream_scope,
        low_io_scope,
        command_retry_scope,
        state_clear_scope,
        mode_state_scope,
        stream_busy_scope,
        current_latency_scope,
        instant_switch_scope,
        stale_error_scope,
        version_scope,
        boot_scope,
        f"- Patched self-loop vector entries: `{vector_count}`.",
        ms_resource_scope,
        sp_resource_scope,
        language_name_scope,
        "- True add-only language menu activation is not patched because the hardcoded language table has no confirmed spare slot.",
        "",
        "## Hashes",
        "",
        f"- Source SHA-256: `{sha256_bytes(source_data)}`",
        f"- Output SHA-256: `{sha256_bytes(output_data)}`",
        f"- Source size: `{len(source_data)}` bytes",
        f"- Output size: `{len(output_data)}` bytes",
        "",
        "## Byte patches",
        "",
        "| Offset | Size | Before | After | Reason |",
        "|---:|---:|---|---|---|",
    ]
    for record in records:
        lines.append(
            f"| `0x{record.offset:05x}` | {len(record.after)} | "
            f"`{record.before.hex(' ')}` | `{record.after.hex(' ')}` | "
            f"{record.reason} |"
        )

    write_text_lf(OUT_REPORT, "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        default=DEFAULT_PROFILE,
        help="patch profile to generate",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="optional isolated output directory instead of firmware-candidates/v4.0.1-beta",
    )
    return parser.parse_args()


def main() -> int:
    global OUT_DIR, OUT_BIN, OUT_SYSTEM, OUT_REPORT, OUT_SUMS
    args = parse_args()
    if args.out_dir is not None:
        OUT_DIR = args.out_dir
        OUT_BIN = OUT_DIR / "DM303V4.0.1-beta.bin"
        OUT_SYSTEM = OUT_DIR / "system"
        OUT_REPORT = OUT_DIR / "PATCH-REPORT.md"
        OUT_SUMS = OUT_DIR / "SHA256SUMS.txt"
    profile = args.profile
    fault_reset = bool(PROFILES[profile]["fault_reset"])
    runtime_patches = bool(PROFILES[profile]["runtime_patches"])
    runtime_patch_profile = PROFILES[profile].get("runtime_patch_profile")
    relay_settle_profile = PROFILES[profile]["relay_settle_profile"]
    mode_switch_profile = PROFILES[profile]["mode_switch_profile"]
    stream_recovery_profile = PROFILES[profile].get("stream_recovery_profile")
    low_io_timeout_profile = PROFILES[profile].get("low_io_timeout_profile")
    low_io_wrapper_profile = PROFILES[profile].get("low_io_wrapper_profile")
    command_retry_profile = PROFILES[profile].get("command_retry_profile")
    stream_state_clear_profile = PROFILES[profile].get("stream_state_clear_profile")
    mode_state_clear_profile = PROFILES[profile].get("mode_state_clear_profile")
    stream_busy_gate_profile = PROFILES[profile].get("stream_busy_gate_profile")
    current_switch_latency_profile = PROFILES[profile].get("current_switch_latency_profile")
    instant_switch_profile = PROFILES[profile].get("instant_switch_profile")
    stale_error_gate_profile = PROFILES[profile].get("stale_error_gate_profile")
    version_patch_profile = PROFILES[profile].get("version_patch_profile")
    language_name_patch = PROFILES[profile].get("language_name_patch", True)
    boot_logo_delay = bool(PROFILES[profile]["boot_logo_delay"])

    source_data = SOURCE.read_bytes()
    source_hash = sha256_bytes(source_data)
    if source_hash != SOURCE_SHA256:
        raise SystemExit(
            f"Refusing to patch unexpected source hash: {source_hash}"
        )

    if fault_reset:
        if source_data[FAULT_BLOCK_OFFSET : FAULT_BLOCK_OFFSET + FAULT_BLOCK_SIZE] != ORIGINAL_FAULT_BLOCK:
            raise SystemExit("Refusing to patch: fault handler block does not match expected V4.0 bytes")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_SYSTEM.mkdir(parents=True, exist_ok=True)

    image = bytearray(source_data)
    records: list[PatchRecord] = []

    vector_offsets: list[int] = []
    if fault_reset:
        vector_offsets = find_self_loop_vectors(source_data)
        if not vector_offsets:
            raise SystemExit("No self-loop vectors found; refusing to patch")

        for entry_offset in vector_offsets:
            before_value = u32_at(source_data, entry_offset)
            if before_value == FAULT_STUB_VECTOR:
                continue
            records.append(
                patch_bytes(
                    image,
                    entry_offset,
                    FAULT_STUB_VECTOR.to_bytes(4, "little"),
                    "redirect self-loop exception/IRQ vector to shared reset-recovery stub",
                )
            )

        records.append(
            patch_bytes(
                image,
                FAULT_BLOCK_OFFSET,
                FAULT_RESET_STUB,
                "replace permanent fault/default loops with SCB_AIRCR SYSRESETREQ stub",
            )
        )

    version_patches = VERSION_PATCHES_BY_PROFILE.get(version_patch_profile, VERSION_PATCHES)
    for offset, replacement in version_patches.items():
        records.append(
            patch_bytes(
                image,
                offset,
                replacement,
                "preserve model ID and mark candidate version as V4.0.1 beta",
            )
        )

    if language_name_patch:
        for offset, (expected, replacement, reason) in LANGUAGE_NAME_PATCHES.items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch language-name guard at 0x{offset:05x}: "
                    f"expected {expected!r}, got {before!r}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if runtime_patches:
        runtime_patch_set = RUNTIME_ANTI_FREEZE_PATCHES_BY_PROFILE[
            runtime_patch_profile or "full"
        ]
        for offset, (replacement, reason) in runtime_patch_set.items():
            before = bytes(image[offset : offset + len(replacement)])
            if before != b"\xfe\xe7":
                raise SystemExit(
                    f"Refusing to patch anti-freeze guard at 0x{offset:05x}: "
                    f"unexpected bytes {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if relay_settle_profile is not None:
        for offset, (expected, replacement, reason) in RELAY_SETTLE_PATCHES[relay_settle_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch relay-settle guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if mode_switch_profile is not None:
        for offset, (expected, replacement, reason) in MODE_SWITCH_PATCHES[mode_switch_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch mode-switch guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if stream_recovery_profile is not None:
        for offset, (expected, replacement, reason) in STREAM_RECOVERY_PATCHES[stream_recovery_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch stream-recovery guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if low_io_timeout_profile is not None:
        for offset, (expected, replacement, reason) in LOW_IO_TIMEOUT_PATCHES[low_io_timeout_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch low-IO timeout guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if low_io_wrapper_profile is not None:
        for offset, (expected, replacement, reason) in LOW_IO_WRAPPER_PATCHES[low_io_wrapper_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch low-IO wrapper guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if command_retry_profile is not None:
        for offset, (expected, replacement, reason) in COMMAND_RETRY_PATCHES[command_retry_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch command-retry guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if stream_state_clear_profile is not None:
        for offset, (expected, replacement, reason) in STREAM_STATE_CLEAR_PATCHES[stream_state_clear_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch stream-state clear guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if mode_state_clear_profile is not None:
        for offset, (expected, replacement, reason) in MODE_STATE_CLEAR_PATCHES[mode_state_clear_profile].items():
            after = replacement() if callable(replacement) else replacement
            if len(after) != len(expected):
                raise SystemExit(
                    f"Refusing to patch mode-state clear at 0x{offset:05x}: "
                    f"expected replacement length {len(expected)}, got {len(after)}"
                )
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch mode-state clear guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, after, reason))

    if stream_busy_gate_profile is not None:
        for offset, (expected, replacement, reason) in STREAM_BUSY_GATE_PATCHES[stream_busy_gate_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch stream busy gate at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if current_switch_latency_profile is not None:
        for offset, (expected, replacement, reason) in CURRENT_SWITCH_LATENCY_PATCHES[current_switch_latency_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch current-switch latency guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if instant_switch_profile is not None:
        for offset, (expected, replacement, reason) in INSTANT_SWITCH_PATCHES[instant_switch_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch instant-switch guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if stale_error_gate_profile is not None:
        for offset, (expected, replacement, reason) in STALE_ERROR_GATE_PATCHES[stale_error_gate_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch stale-error gate at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if boot_logo_delay:
        original_call = encode_thumb_bl(LOAD_BASE + BOOT_LOGO_DELAY_CALL_OFFSET, BOOT_LOGO_ORIGINAL_LOAD)
        before = bytes(image[BOOT_LOGO_DELAY_CALL_OFFSET : BOOT_LOGO_DELAY_CALL_OFFSET + len(original_call)])
        if before != original_call:
            raise SystemExit(
                f"Refusing to patch boot-logo call guard at 0x{BOOT_LOGO_DELAY_CALL_OFFSET:05x}: "
                f"expected {original_call.hex(' ')}, got {before.hex(' ')}"
            )
        stub_guard = bytes(
            image[BOOT_LOGO_DELAY_STUB_OFFSET : BOOT_LOGO_DELAY_STUB_OFFSET + BOOT_LOGO_STUB_GUARD_SIZE]
        )
        if stub_guard != b"\x00" * BOOT_LOGO_STUB_GUARD_SIZE:
            raise SystemExit(
                f"Refusing to patch boot-logo stub guard at 0x{BOOT_LOGO_DELAY_STUB_OFFSET:05x}: "
                "candidate code cave is not empty"
            )
        stub = build_boot_logo_delay_stub()
        if len(stub) > BOOT_LOGO_STUB_GUARD_SIZE:
            raise SystemExit("Boot-logo delay stub is larger than the guarded code cave")
        wrapper_call = encode_thumb_bl(
            LOAD_BASE + BOOT_LOGO_DELAY_CALL_OFFSET,
            LOAD_BASE + BOOT_LOGO_DELAY_STUB_OFFSET,
        )
        records.append(
            patch_bytes(
                image,
                BOOT_LOGO_DELAY_CALL_OFFSET,
                wrapper_call,
                f"{profile}: route LOGO-1 resource load through boot stabilization delay wrapper",
            )
        )
        records.append(
            patch_bytes(
                image,
                BOOT_LOGO_DELAY_STUB_OFFSET,
                stub,
                f"{profile}: call original LOGO-1 loader, wait 200 ticks, then return to boot loader",
            )
        )

    output_data = bytes(image)
    OUT_BIN.write_bytes(output_data)

    stage_text_resources = bool(PROFILES[profile].get("stage_text_resources", True))
    if stage_text_resources and MS_TEXT.exists():
        shutil.copy2(MS_TEXT, OUT_SYSTEM / "TEXT_MS.DAT")
    sp_text_source = PROFILES[profile].get("sp_text_source")
    if not stage_text_resources:
        pass
    elif sp_text_source == "safe-sp-layout":
        if SAFE_SP_TEXT.exists():
            shutil.copy2(SAFE_SP_TEXT, OUT_SYSTEM / "TEXT_SP.DAT")
    elif SP_TEXT.exists():
        shutil.copy2(SP_TEXT, OUT_SYSTEM / "TEXT_SP.DAT")

    write_report(
        records,
        source_data,
        output_data,
        profile,
        fault_reset,
        runtime_patches,
        runtime_patch_profile,
        relay_settle_profile,
        mode_switch_profile,
        stream_recovery_profile,
        low_io_timeout_profile,
        low_io_wrapper_profile,
        command_retry_profile,
        stream_state_clear_profile,
        mode_state_clear_profile,
        stream_busy_gate_profile,
        current_switch_latency_profile,
        instant_switch_profile,
        stale_error_gate_profile,
        version_patch_profile,
        boot_logo_delay,
        len(vector_offsets),
    )

    sums = [
        f"{sha256_file(OUT_BIN)}  {OUT_BIN.name}",
    ]
    ms_candidate = OUT_SYSTEM / "TEXT_MS.DAT"
    if ms_candidate.exists():
        sums.append(f"{sha256_file(ms_candidate)}  system/TEXT_MS.DAT")
    sp_candidate = OUT_SYSTEM / "TEXT_SP.DAT"
    if sp_candidate.exists():
        sums.append(f"{sha256_file(sp_candidate)}  system/TEXT_SP.DAT")
    write_text_lf(OUT_SUMS, "\n".join(sums) + "\n")

    print(f"source={SOURCE}")
    print(f"source_sha256={source_hash}")
    print(f"output={OUT_BIN}")
    print(f"profile={profile}")
    print(f"output_size={len(output_data)}")
    print(f"output_sha256={sha256_file(OUT_BIN)}")
    print(f"patched_vectors={len(vector_offsets)}")
    print(f"patch_records={len(records)}")
    print(f"report={OUT_REPORT}")
    print("safety_note=candidate only; do not flash before bench/recovery validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
