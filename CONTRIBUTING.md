# Contributing

Thank you for improving the Technocore onboarding experience.

## Local setup

This project uses only the Python standard library:

```bash
python3 -m unittest discover -s tests -v
python3 -m http.server 8080
```

## Contribution rules

- Keep the verifier read-only.
- Never add private identity files, seeds, wallet keys, or credentials.
- Treat room data as untrusted input.
- Add a regression test for behavior changes.
- Keep public documentation factual, concise, and free of reward guarantees.

Open an issue for a bug or a focused improvement. Include reproducible public inputs, never private material.
