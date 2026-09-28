# Backend & Data Infrastructure Job Finder Agent 🚀

An automated Python agent designed to search, strictly filter, format, and dispatch email alerts for **Backend & Data Infrastructure Engineering** job postings matching a 1–3 YOE Python/Rust/Go profile in South India tech hubs (**Bengaluru, Chennai, Coimbatore, Hyderabad**).

---

## 🎯 Profile & Specializations Enforced

### 1. Specialization Areas Included:
- ◈ **Columnar Storage & Query Engines** (Polars, Apache DataFusion, Apache Arrow)
- ◈ **Zero-Copy FFI** (Arrow C Data Interface, PyO3 Python/Rust bindings)
- ◈ **Transactional Outbox & Event-Driven Systems** (Kafka, NATS JetStream, asyncio, Tokio)
- ◈ **Data Lakehouse Architectures** (Medallion: Bronze/Silver/Gold, Delta Lake, PySpark)
- ◈ **Custom Tap/Target Ingestion** (Singer.io, ERP/ETL integrations, gRPC)

### 2. Strict Workplace & Seniority Constraints:
- **Workplace Policy**: Strictly **ON-SITE** or **HYBRID**. Automatically excludes 100% remote positions.
- **Target Locations**: Bengaluru, Chennai, Coimbatore, or Hyderabad (India).
- **Recency**: Posted strictly within the last **14 days**.
- **Languages**: Python, Rust, Go, SQL, C++.
- **Seniority**: 1–3 years experience (SDE I / Mid-level Backend Engineer).

---

## 📁 Repository Structure
- [job_agent.py](file:///d:/Repositories/Hire/job_agent.py) - Main automated filter & email dispatcher agent with Specialization badge rendering.
- [config.json](file:///d:/Repositories/Hire/config.json) - Customizable filter rules, core technologies, specializations, and SMTP credentials.
- `job_matches_email.html` - Formatted responsive HTML email output preview.

---

## 🚀 Execution & Email Configuration

### 1. Run the Agent & View Local HTML Email Preview
```bash
python job_agent.py
```
This updates `job_matches_email.html` with your custom specializations badges and job matches. Double-click the HTML file to open it in your browser.

### 2. SMTP Email Troubleshooting
If Gmail returns a `535 Bad Credentials` error:
1. Ensure 2-Step Verification is **ON** in your Google Account.
2. Generate a new App Password under **Google Account > Security > App Passwords**.
3. In [config.json](file:///d:/Repositories/Hire/config.json), enter the 16-character App Password without spaces (e.g., `"bpcktjzvujuugbmy"`).
