# ZilantFS

`ZilantFS` mounts a `.zil` container as a normal directory. Files inside the mount
point are transparently decrypted or encrypted using the Zilant Prime Core crypto
engine.

## Usage

```bash
zilant mount secret.zil mnt -p -
# work with files
zilant umount mnt
```

Install optional dependencies with:

```bash
pip install "zilant-prime-core[zilfs]"
```

The implementation relies on **fusepy** on Unix and **pywinfspy** on Windows.

## Requirements

- **Linux**: install `fuse3` and `libfuse3-dev` packages.
- **macOS**: install `macfuse` and `fusepy` via Homebrew.
- **Windows**: install [WinFSP](https://winfsp.dev/) and the Python package `pywinfspy`.

## Examples

Synchronise a directory using `rsync`:

```bash
zilant mount secret.zil mnt -p mypwd
rsync -av mnt/ backup/
zilant umount mnt
```

Use TimeMachine (macOS) to back up the mounted folder:

```bash
zilant mount data.zil /Volumes/Secure -p mypwd
tmutil startbackup --destination /Volumes/Secure
```

## Security notes

- Containers are integrity checked on mount. On failure the filesystem is mounted read‑only and a warning is logged.
- Decoy mode (`--decoy-profile minimal`) exposes fake files without touching the real container.
