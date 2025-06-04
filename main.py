from attest import attestation_check

if __name__ == "__main__":
    if not attestation_check():
        print("Local mode – TPM отсутствует")
    else:
        print("TPM attestation passed")
