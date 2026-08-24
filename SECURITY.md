# Security policy

## Scope

This project handles public Technocore room data only. The verifier is not a signer and should never require a private seed, wallet key, PEM file, or credential.

## Reporting

Do not open a public issue containing private keys, credentials, or sensitive personal data. Use GitHub's private vulnerability reporting for the repository when available. If it is unavailable, contact the maintainers privately before disclosing details.

## Safe-use rules

- Keep signing identities outside this repository.
- Review the staged file list before any commit.
- Treat room messages, note values, room names, and topics as untrusted data.
- Do not assume a signed DID proves a person's legal identity or a reward entitlement.
