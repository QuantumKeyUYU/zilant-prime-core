import pytest
from src.vdf import generate_vdf, generate_partial_proofs, verify_partial_proof

def test_generate_vdf():
    seed = b"test_seed"
    steps = 100
    proof = generate_vdf(seed, steps)
    assert isinstance(proof, bytes) and len(proof) == 32

def test_generate_partial_proofs():
    seed = b"test_seed"
    steps = 100
    interval = 25
    proofs = generate_partial_proofs(seed, steps, interval)

    assert len(proofs) == 5  # (0,25,50,75,100)
    assert proofs[0] == seed
    assert 100 in proofs

def test_verify_partial_proof_correct():
    seed = b"test_seed"
    steps = 50
    proofs = generate_partial_proofs(seed, 100, 50)
    assert verify_partial_proof(proofs[0], proofs[50], steps) == True

def test_verify_partial_proof_incorrect():
    seed = b"test_seed"
    wrong_proof = b"wrong_proof_value"
    steps = 50
    assert verify_partial_proof(seed, wrong_proof, steps) == False

@pytest.mark.parametrize("steps, interval", [(100, 10), (200, 50), (150, 30)])
def test_partial_proof_chain(steps, interval):
    seed = b"another_test_seed"
    proofs = generate_partial_proofs(seed, steps, interval)
    checkpoints = sorted(proofs.keys())

    for i in range(len(checkpoints) - 1):
        start = checkpoints[i]
        end = checkpoints[i+1]
        assert verify_partial_proof(proofs[start], proofs[end], end - start) == True
