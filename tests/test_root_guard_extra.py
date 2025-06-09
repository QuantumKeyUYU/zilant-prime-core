# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

import zilant_prime_core.utils.root_guard as rg


def test_all_root_checks(monkeypatch):
    monkeypatch.setattr(rg, "_check_uid_gid", lambda: True)
    monkeypatch.setattr(rg, "_check_root_binaries", lambda: False)
    monkeypatch.setattr(rg, "_check_mounts", lambda: False)
    monkeypatch.setattr(rg, "_check_selinux", lambda: False)
    monkeypatch.setattr(rg, "_check_ptrace", lambda: False)
    monkeypatch.setattr(rg, "_check_ld_preload", lambda: False)
    assert rg.is_device_rooted() is True

    monkeypatch.setattr(rg, "_check_uid_gid", lambda: False)
    monkeypatch.setattr(rg, "_check_root_binaries", lambda: True)
    assert rg.is_device_rooted() is True

    monkeypatch.setattr(rg, "_check_root_binaries", lambda: False)
    monkeypatch.setattr(rg, "_check_mounts", lambda: True)
    assert rg.is_device_rooted() is True

    monkeypatch.setattr(rg, "_check_mounts", lambda: False)
    monkeypatch.setattr(rg, "_check_selinux", lambda: True)
    assert rg.is_device_rooted() is True

    monkeypatch.setattr(rg, "_check_selinux", lambda: False)
    monkeypatch.setattr(rg, "_check_ptrace", lambda: True)
    assert rg.is_device_rooted() is True

    monkeypatch.setattr(rg, "_check_ptrace", lambda: False)
    monkeypatch.setattr(rg, "_check_ld_preload", lambda: True)
    assert rg.is_device_rooted() is True

    # Всё False — безопасно
    monkeypatch.setattr(rg, "_check_ld_preload", lambda: False)
    assert rg.is_device_rooted() is False
