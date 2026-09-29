# Backend & Data Infrastructure Job Finder Agent 🚀

An automated Python agent designed to search, strictly filter, format, and dispatch email alerts for **Backend, Data Infrastructure, Systems, and AI/ML Engineering** job postings matching a 1–3 YOE Python/Rust/Go profile in South India tech hubs (**Bengaluru, Chennai, Coimbatore, Hyderabad**).

---

## 🌟 What's New: Multi-Stream Ingestion & Dream Companies Priority

### 1. 🏢 Dream Companies Priority Tiering (`dream_companies`)
- Configured in [config.json](file:///d:/Repositories/Hire/config.json), [config_AIML.json](file:///d:/Repositories/Hire/config_AIML.json), and [config_rust_systems.json](file:///d:/Repositories/Hire/config_rust_systems.json).
- **Direct Job Requisition Endpoints**: Instead of linking to generic `/careers` landing pages, the agent resolves directly to the exact job requisition and application page (e.g., Ashby requisition UUIDs, Greenhouse `gh_jid` URLs, Lever application links, and Instahyre direct opening posts).
- **Automated ATS Integration**: Directly queries live ATS APIs (Greenhouse, Lever, Ashby) for your target dream companies (e.g., Sarvam AI, Databricks, Cloudflare, Razorpay, CRED, PhonePe, Hasura, Zepto, etc.).
- **Strict Priority Ordering**: Matches from your Dream Companies are positioned **first** (Tier 1) at the top of the email digest and console summary, followed by top verified opportunities from other trusted sources (Tier 2).

### 2. 🌐 Multi-Stream Trusted Sources
The agent dynamically aggregates from verified developer sources:
1. **Dream Companies ATS Live Stream**: Real-time Ashby (`api.ashbyhq.com`), Greenhouse (`boards-api.greenhouse.io`), and Lever (`api.lever.co`) endpoints with zero intermediary lag.
2. **Google Jobs & Regional Tech Hiring RSS Stream**: Real-time hiring feeds for Bengaluru, Hyderabad, Chennai.
3. **Hacker News Y Combinator Jobs**: Direct founder/engineer postings from YC startups.
4. **Remotive Live Developer API**: Verified software engineering listings.
5. **Arbeitnow Developer API**: Verified engineering roles.
6. **Curated Product Tech Corpus**: High-affinity product tech startups tailored to the loaded configuration profile with direct application links.

### 3. 🎨 Executive & Cleaner Email Template
- **Zero Collision Layout**: Replaced fragile CSS flex layouts with robust table headers so location pills (`📍 On-site • Bengaluru`) never clash or overlap with job titles across email clients.
- **Luxury Dream Company Highlights**: Distinctive amber/gold badges (`⭐ Dream Company Priority`), left gold accents, and direct `Apply Direct to Opening →` CTA buttons.
- **Direct Requisition Linking**: All CTAs take you directly to the specific job requisition application form instead of generic company portals.
- **Trusted Source Attribution**: Verified badges (`⚡ Ashby ATS`, `⚡ Greenhouse ATS`, `🏢 Direct Requisition Endpoint`, etc.).
- **Executive Summary Header**: Live breakdown of Dream Company vs. Trusted Source match counts.

---

## 🎯 Profile & Specializations Enforced

### 1. Specialization Areas Included:
- ◈ **Columnar Storage & Query Engines** (Polars, Apache DataFusion, Apache Arrow)
- ◈ **Zero-Copy FFI** (Arrow C Data Interface, PyO3 Python/Rust bindings)
- ◈ **Transactional Outbox & Event-Driven Systems** (Kafka, NATS JetStream, asyncio, Tokio)
- ◈ **Data Lakehouse Architectures** (Medallion: Bronze/Silver/Gold, Delta Lake, PySpark)
- ◈ **Custom Tap/Target Ingestion** (Singer.io, ERP/ETL integrations, gRPC)

### 2. Strict Workplace & Seniority Constraints:
- **Workplace Policy**: Strictly **ON-SITE** or **HYBRID**. Automatically excludes 100% remote positions (unless enabled in profile).
- **Target Locations**: Bengaluru, Chennai, Coimbatore, or Hyderabad (India).
- **Recency**: Posted strictly within the last **14 days**.
- **Languages**: Python, Rust, Go, SQL, C++.
- **Seniority**: 1–3 years experience (SDE I / Mid-level Backend Engineer). Automatically filters out executive/director titles.

---

## 📁 Repository Structure
- [job_agent.py](file:///d:/Repositories/Hire/job_agent.py) - Main automated filter & multi-stream email dispatcher agent.
- [config.json](file:///d:/Repositories/Hire/config.json) - Backend & Data Infrastructure configuration with Dream Companies & stream toggles.
- [config_AIML.json](file:///d:/Repositories/Hire/config_AIML.json) - AI/ML & LLM Platform engineering configuration.
- [config_rust_systems.json](file:///d:/Repositories/Hire/config_rust_systems.json) - Rust & High-Throughput systems configuration.
- `job_matches_email.html` - Formatted responsive HTML email output preview.

---

## 🚀 Execution & CLI Options

### 1. Run with Default Config:
```bash
python job_agent.py
```

### 2. Run with Specific Config Profiles:
```bash
python job_agent.py config=config_AIML.json
python job_agent.py config=config_rust_systems.json
```

Double-click `job_matches_email.html` (or `job_matches_config_AIML.html`) to preview the email in any browser.

---

## 📧 Gmail SMTP Setup & Configuration Guide

To automatically dispatch formatted email digests to your inbox, the agent uses secure SMTP via **Google App Passwords**.

> [!NOTE]
> Google deprecated standard password logins for third-party scripts. Your regular Gmail password will return a `535 5.7.8 Bad Credentials` error. You must generate a dedicated **16-character App Password**.

### 🛠️ Step-by-Step Instructions:

1. **Enable 2-Step Verification**:
   - Go to your [Google Account Security Settings](https://myaccount.google.com/security).
   - Under **How you sign in to Google**, ensure **2-Step Verification** is turned **ON**. *(App Passwords cannot be generated if 2-Step Verification is off).*

2. **Generate an App Password**:
   - Navigate directly to [Google App Passwords](https://myaccount.google.com/apppasswords) (or search *"App passwords"* in the top search bar of your Google Account).
   - Enter an app name to identify this project (e.g., `JobFinderAgent` or `HireAgent`).
   - Click **Create**. Google will display a 16-character passcode in a yellow box (e.g., `abcd efgh ijkl mnop`).

3. **Configure [config.json](file:///d:/Repositories/Hire/config.json)**:
   - Paste the 16 characters into `"sender_password"` **without spaces**:
   ```json
   "email_settings": {
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 587,
     "sender_email": "your_email@gmail.com",
     "sender_password": "abcdefghijklmnop",
     "recipient_email": "target_email@gmail.com",
     "enable_smtp": true,
     "save_html_preview": true
   }
   ```

### 🔍 SMTP Settings Reference:

| Field | Value | Purpose |
| :--- | :--- | :--- |
| `smtp_server` | `"smtp.gmail.com"` | Google's official outbound SMTP mail host. |
| `smtp_port` | `587` | Standard TLS port for secure STARTTLS communication. |
| `sender_email` | `"your_email@gmail.com"` | The Google account that created the App Password. |
| `sender_password` | `"16_char_app_password"` | 16-character App Password without spaces. |
| `recipient_email` | `"target_email@gmail.com"` | Destination inbox for the daily digests. |
| `enable_smtp` | `true` or `false` | Set to `false` if you only want local HTML previews without sending emails. |
| `save_html_preview`| `true` | Always writes `job_matches_email.html` locally for browser inspection. |

### 💡 Common Troubleshooting Tips:
- **`535 5.7.8 Username and Password not accepted`**: Ensure you copied the 16 characters with all whitespace removed. Also ensure `sender_email` matches the account where the App Password was created.
- **Testing without sending emails**: Set `"enable_smtp": false` in the active config. The agent will run all scans, filters, and save the local HTML preview without connecting to the mail server.
