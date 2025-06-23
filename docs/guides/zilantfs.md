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
