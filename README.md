# envchain-cli

A CLI tool for managing and encrypting per-project environment variable sets locally.

---

## Installation

```bash
pip install envchain-cli
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envchain-cli
```

---

## Usage

**Initialize a new env chain for your project:**
```bash
envchain init myproject
```

**Add a variable to a chain:**
```bash
envchain set myproject DATABASE_URL=postgres://localhost/mydb
```

**Run a command with a chain's variables injected:**
```bash
envchain run myproject -- python app.py
```

**List all chains:**
```bash
envchain list
```

**Show variables in a chain:**
```bash
envchain show myproject
```

Variables are encrypted at rest using a master password and stored locally in `~/.envchain/`.

---

## Features

- AES-256 encrypted storage of environment variables
- Per-project isolation of variable sets
- Simple injection of variables into any subprocess
- No cloud dependencies — fully local

---

## License

This project is licensed under the [MIT License](LICENSE).