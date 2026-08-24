# Deployment

The guide is a dependency-free static page. The verifier is a Python command-line tool and does not require a server.

## Local preview

From the project root:

```bash
python3 -m http.server 8080
```

Open `http://127.0.0.1:8080/`.

## Static hosting

The repository can be hosted by GitHub Pages or another static-file host. Publish the repository root as the site directory. No environment variables are required, and no private identity files belong in the published tree.

## Post-deployment checks

- Open the home page and confirm the hero, trust-boundary diagram, and mobile layout render.
- Open the contribution and troubleshooting documents.
- Run the Python test suite locally or through CI.
- Confirm that no `.env`, `*.pem`, `*.key`, or seed file is present in the published files.
