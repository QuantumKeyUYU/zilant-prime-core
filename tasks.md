# Codex Task List

## New tasks package

This file contains tasks from the "Сделай-ка, Codex!" package.

| Block | Task | Done criteria |
| --- | --- | --- |
| SEC-1 | Secrets / CI: Find all `echo ${{ secrets.* }}` in `.github/workflows/**.yml`, replace with `echo "::add-mask::${{ secrets.NAME }}"` or delete. | `grep -R "echo ${{ secrets" .github` |
| SEC-2 | Secrets: Add gitleaks in pre-commit and GitHub Actions (`zricethezav/gitleaks-action@v2.3.2`). | PR with new job passes without leaks |
| CI-1 | Matrix: Merge `lint-fast` and `tests-full` into one `ci.yml` with matrix `os=[ubuntu,windows,macos]`, `python=[3.8,3.9,3.10,3.11]`. | All 12 combos green, step time ≤ 12 min |
| CI-2 | Nightly fuzz: Create `fuzz-nightly` job (Atheris) with cron `"0 3 * * *"`, publish artifact `atheris-report.html`. | Artifact available, workflow doesn't fail |
| CI-3 | Codecov: In `tests-full` add step `codecov/codecov-action@v3`, enable PR comments. | Diff comment with coverage link visible |
| CI-4 | SCA scan: Fix Trivy job skipping. Condition should be `if: github.event_name == 'pull_request'`. | Job runs on PR |
| DOC-1 | Sphinx strict: In `docs/conf.py` set `nitpicky = True`, `nitpick_ignore = []`, and build with `-W`. | `make -C docs html` fails on warnings |
| DOC-2 | How-to: Add two MD guides in `docs/how-to/`:
 1. `tor_proxy.md` – running CLI traffic via Tor.
 2. `ring_signatures.md` – generate/verify PQ-ring signatures.
 Each includes at least 2 code blocks and a Mermaid diagram. | Guides present |
| PKG-1 | PEP-621 finish: remove `setup.cfg` and `requirements*.txt`, use `pyproject.toml` with `[project.optional-dependencies]` (`dev`, `docs`, `tests`). | `pip install .[dev]` and `pip install .[docs]` work |
| PKG-2 | Win wheel: In `packaging.yml` add Windows job `build-wheel`, upload artifact `*.whl` using `actions/upload-artifact@v4`. | Artifact available for each PR |
| PKG-3 | SBOM: Add `cyclonedx-python` step after `build-wheel` and upload artifact `sbom.json`. | File exists and is valid (`jq .version`) |
| QA-1 | Logging: Replace `print()` with logging at INFO level in `src/**.py`. | `grep -R "print(" src` shows none |
| QA-2 | Typing: Enable `mypy --strict` in pre-commit, ignore only `cryptography`, `hpke`, `oqs`. | `mypy` ends with 0 errors |
| FEAT-X | Placeholder: Create empty scaffolds for all "New features" under `src/feature/` (directories, `__init__.py`, `TODO.md`). | Modules import without errors |

## Completed
- SEC-1: no workflow secrets echoed
- SEC-2: no tempfile.mkdtemp usage
- CI-1: unified matrix workflow running tests and linters
- CI-2: nightly fuzz job uploads atheris-report.html artifacts
- CI-3: Codecov uploads coverage and comments on PRs
- CI-4: Trivy SCA scan runs on push and pull_request
