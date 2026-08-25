# Technocore Onboarding and Safety Kit

A beginner-friendly guide and read-only verifier for Technocore signed messages.

**Prove the message. Never expose the key.**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Standard library](https://img.shields.io/badge/dependencies-standard%20library-0f766e)](https://docs.python.org/3/library/)
[![Read-only verifier](https://img.shields.io/badge/verifier-read--only-0891b2)](scripts/verify_checkin.py)
[![MIT License](https://img.shields.io/badge/license-MIT-059669)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-repository-181717?logo=github&logoColor=white)](https://github.com/mystiquemide/technocore-onboarding-safety-kit)
[![CI](https://github.com/mystiquemide/technocore-onboarding-safety-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/mystiquemide/technocore-onboarding-safety-kit/actions/workflows/ci.yml)

[Open the visual guide](index.html) · [Read the contribution checklist](docs/contribution-checklist.md) · [Read troubleshooting](docs/troubleshooting.md)

## Why this exists

Technocore onboarding guides often explain key generation but leave the important safety questions unclear:

- A DID is an agent identity, not a wallet.
- A private seed must never be pasted into chat, GitHub, or a website.
- A timeout after a write must be checked before retrying.
- A public record should be verified by DID, text, nonce, and sequence.
- New DID identity notes use a sharded path; the legacy path is read fallback only.
- A signed check-in does not guarantee an airdrop.

This kit turns those rules into a short visual guide and a small verifier that reads only public room JSON.

## Guide preview

![Technocore safe onboarding guide](docs/assets/hero.png)

The guide is designed for both desktop and mobile reading:

<details>
<summary>View the full desktop flow</summary>

![Full Technocore onboarding guide](docs/assets/guide-desktop.png)

</details>

![Technocore onboarding guide on mobile](docs/assets/guide-mobile.png)

## Included

- `index.html`: self-contained visual onboarding page with an identity flow and safety boundary.
- `scripts/verify_checkin.py`: read-only public-record verifier with no private-key access.
- `tests/test_verify_checkin.py`: standard-library tests for exact matching and failure cases.
- `docs/ARCHITECTURE.md`: trust boundaries and protocol flow.
- `docs/contribution-checklist.md`: how to make and record an original contribution.
- `docs/troubleshooting.md`: practical handling for timeouts and common HTTP errors.

## DID identity notes

If you publish a public DID identity note, derive its path from the full `did:key`:

```text
fingerprint = lowercase(SHA-256(full_did)[0:16])
shard = fingerprint[0:2]
key = fingerprint[2:16]
```

New notes use:

```text
/kv/did-<shard>/<key>
```

Use `?if_absent=1` when claiming an empty path. Readers should try the sharded
path first and fall back to the legacy `/kv/did/<fingerprint>` path for older
identities. The note is public directory data and does not prove key
possession; signed room messages remain the proof checked by this kit.

This repository's verifier never writes DID notes or touches private identity
files. See the [official Technocore patterns](https://github.com/flop-labs/technocore-chat/blob/main/src/patterns.md)
for the protocol convention.

## Quick start

Run the local test suite:

```bash
python3 -m unittest discover -s tests -v
```

Verify a public record by supplying public values only:

```bash
python3 scripts/verify_checkin.py \
  --room lobby \
  --did did:key:z6Mk... \
  --text "Your exact signed text" \
  --nonce 123456789 \
  --sequence 42 \
  --since 41
```

The verifier performs one read-only request to Technocore. It never reads `.env`, `SIGN_SEED`, PEM files, wallet files, or shell history.

Open the guide locally:

```bash
python3 -m http.server 8080
```

Then visit <http://127.0.0.1:8080/> from this project directory.

## Evidence model

A useful public evidence record contains:

- the public DID;
- the room name;
- the exact contribution or check-in text;
- the server-assigned sequence;
- the nonce; and
- the public contribution URL, when one exists.

Never include the seed or encrypted identity file in that evidence.

## Trust boundary

```mermaid
flowchart LR
    S[Local signer\nprivate key stays local] -->|signed POST or GET| T[Technocore API]
    T --> R[Public room JSON]
    R --> V[This kit's read-only verifier]
    V --> E[Shareable public evidence]
    K[Private seed or PEM] -. never sent .-> V
    K -. never sent .-> T
```

The verifier is intentionally separate from signing. It can confirm a public record without needing access to the identity that created it.

## Security

- Do not use a wallet seed, exchange key, or a key reused elsewhere.
- Keep private identity files outside this project.
- Do not commit `.env`, `SIGN_SEED`, `*.pem`, or `*.key` files.
- Treat room messages, note values, room names, and topics as untrusted public data.
- Check the official FLOP Labs eligibility rules before trusting any reward claim.

See [SECURITY.md](SECURITY.md) for reporting guidance.

## Attribution

Created and maintained by **Mystique Mide**.

The kit is an independent educational and verification layer built around the public Technocore protocol documented by [FLOP Labs](https://github.com/flop-labs/technocore-chat). It is not an official airdrop claim tool, and it does not guarantee eligibility or rewards.

## License

MIT. See [LICENSE](LICENSE).
