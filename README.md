<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 360" width="100%" height="auto">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090d16"/>
      <stop offset="50%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e1b4b"/>
    </linearGradient>
    <linearGradient id="textGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#c084fc"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#334155" stroke-width="0.75" stroke-opacity="0.3"/>
    </pattern>
  </defs>

  <rect width="1200" height="360" fill="url(#bg)" rx="16"/>
  <rect width="1200" height="360" fill="url(#grid)" rx="16"/>

  <circle cx="600" cy="130" r="160" fill="#6366f1" opacity="0.12" filter="blur(40px)"/>

  <text x="600" y="110" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700" letter-spacing="4" fill="#38bdf8" text-anchor="middle">HACKATHON SHOWCASE</text>
  <text x="600" y="180" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="58" font-weight="900" letter-spacing="-1" fill="url(#textGrad)" text-anchor="middle">ANIMUSLENS</text>
  <text x="600" y="225" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="18" font-weight="400" fill="#94a3b8" text-anchor="middle">Zero-Server-Key Verification • Client-Side SHA-256 • Ethereum Sepolia</text>

  <g transform="translate(310, 270)">
    <rect x="0" y="0" width="160" height="36" rx="18" fill="#1e293b" stroke="#334155" stroke-width="1"/>
    <text x="80" y="23" font-family="sans-serif" font-size="13" font-weight="600" fill="#f8fafc" text-anchor="middle">⚡ Real-time Checks</text>

    <rect x="180" y="0" width="180" height="36" rx="18" fill="#1e293b" stroke="#334155" stroke-width="1"/>
    <text x="270" y="23" font-family="sans-serif" font-size="13" font-weight="600" fill="#f8fafc" text-anchor="middle">🛡️ Zero Private Keys</text>

    <rect x="380" y="0" width="200" height="36" rx="18" fill="#1e293b" stroke="#334155" stroke-width="1"/>
    <text x="480" y="23" font-family="sans-serif" font-size="13" font-weight="600" fill="#f8fafc" text-anchor="middle">⛽ Fixed Gas Overhead</text>
  </g>
</svg>

<br/><br/>

<p align="center">
  <a href="#-quick-start"><b>Quick Start</b></a> •
  <a href="#-architecture"><b>Architecture</b></a> •
  <a href="#-core-workflows"><b>Workflows</b></a> •
  <a href="#-smart-contract"><b>Smart Contract</b></a> •
  <a href="#-the-team"><b>The Team</b></a>
</p>

</div>

---

### ⚡ At a Glance

| Target Parameter | Traditional Centralized Model | AnimusLens Architecture |
| :--- | :--- | :--- |
| **Trust Vector** | Single central server database | Immutable Ethereum smart contract |
| **Fraud Vulnerability** | Editable PDFs / forged signatures | Tamper-proof 32-byte SHA-256 fingerprint |
| **Key Custody** | Server holds raw administrative keys | **Zero-key backend**: Client signs in MetaMask |
| **Verification Speed** | Days/weeks of manual registrar back-and-forth | **Instant** deterministic checksum comparison |
| **Privacy Footprint** | Raw certificate files uploaded to 3rd parties | Only the digest (`bytes32`) touches the chain |

---

### 🏛 Architecture & Data Flow

```text
[ Issuer Browser ]
       │
       ├─► 1. File selected (PDF/PNG/JPG)
       ├─► 2. Local SHA-256 Digest calculated in-memory
       └─► 3. MetaMask prompts transaction (setCert)
                 │
                 ▼
[ Sepolia Testnet ] ─── Immutable Registry (CertRegistry.sol)
                 ▲
                 │
[ Verifier Web UI ]
       │
       ├─► 1. Drag & drop suspicious file
       ├─► 2. Compute local digest in browser
       └─► 3. Web3 call: getCert(certId) ──► Instant Match / Tamper Flag