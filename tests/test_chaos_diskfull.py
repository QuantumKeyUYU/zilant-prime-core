import subprocess


def test_diskfull_script():
    cp = subprocess.run(["tests/chaos/disk_full_test.sh"], capture_output=True, text=True)
    assert cp.returncode == 0
    assert "Traceback" not in cp.stdout
    assert "Traceback" not in cp.stderr
