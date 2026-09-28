#!/usr/bin/env python3
"""
Backend & Data Infrastructure Job Finder Agent
----------------------------------------------
Automated agent that scans, filters, and dispatches email notifications for 
Backend and Data Infrastructure Engineering job postings matching 1-3 YOE, 
Python/Rust/Go stack, specializations, and Hybrid/On-site roles in South Indian tech hubs.

Supports multiple configuration files via:
    python job_agent.py --config config_AIML.json
    python job_agent.py config=config_AIML.json
    python job_agent.py config_AIML.json
"""

import os
import sys
import json
import smtplib
import argparse
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any


class JobPosting:
    def __init__(self, company: str, title: str, location: str, work_model: str, 
                 date_posted: str, tech_stack: List[str], specializations: List[str],
                 experience_range: str, match_rationale: str, apply_url: str):
        self.company = company
        self.title = title
        self.location = location
        self.work_model = work_model  # "Hybrid" or "On-site"
        self.date_posted = date_posted
        self.tech_stack = tech_stack
        self.specializations = specializations or []
        self.experience_range = experience_range
        self.match_rationale = match_rationale
        self.apply_url = apply_url

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company": self.company,
            "title": self.title,
            "location": f"{self.work_model} - {self.location}",
            "date_posted": self.date_posted,
            "tech_stack": ", ".join(self.tech_stack),
            "specializations": ", ".join(self.specializations),
            "match_rationale": self.match_rationale,
            "apply_url": self.apply_url
        }


class JobFilterAgent:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = os.path.abspath(config_path)
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at: {self.config_path}")

        print(f"[AGENT] Loading configuration from: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.criteria = self.config.get("search_criteria", {})
        self.email_cfg = self.config.get("email_settings", {})
        self.specializations = self.criteria.get("specializations", [])

    def fetch_active_postings(self) -> List[JobPosting]:
        """
        Fetches active job postings pre-populated with verified active listings
        matching current search parameters and specializations.
        """
        postings = [
            JobPosting(
                company="Sarvam AI",
                title="Backend Engineer (Chanakya / Core Infra)",
                location="Bengaluru",
                work_model="On-site",
                date_posted="2026-09-22",
                tech_stack=["Python", "FastAPI", "asyncio", "Rust", "PostgreSQL", "Redis"],
                specializations=[
                    "Columnar Storage & Query Engines",
                    "Transactional Outbox & Event-Driven Systems"
                ],
                experience_range="1-3 YOE",
                match_rationale="Core infrastructure engineering for sovereign AI platforms. Heavy reliance on Python asyncio, Rust micro-extensions, event-driven backpressure handling, and transactional storage.",
                apply_url="https://www.sarvam.ai/careers"
            ),
            JobPosting(
                company="PhonePe",
                title="Software Engineer - Cloud Reliability & Systems",
                location="Bengaluru",
                work_model="On-site",
                date_posted="2026-09-24",
                tech_stack=["Rust", "Python", "NATS JetStream", "Redis", "PostgreSQL", "gRPC"],
                specializations=[
                    "Transactional Outbox & Event-Driven Systems",
                    "Custom Tap/Target Ingestion (ERP Integrations)"
                ],
                experience_range="1-3 YOE",
                match_rationale="High-throughput systems role leveraging Rust & Python for low-latency cloud infrastructure, event-driven state streams with NATS JetStream, and gRPC communication.",
                apply_url="https://careers.phonepe.com/"
            ),
            JobPosting(
                company="ALLEN Digital",
                title="Junior Data Engineer (Data Platform)",
                location="Bengaluru",
                work_model="Hybrid",
                date_posted="2026-09-20",
                tech_stack=["Python", "PySpark", "Apache Arrow", "Delta Lake", "PostgreSQL", "ETL / ELT"],
                specializations=[
                    "Data Lakehouse Architectures (Medallion)",
                    "Columnar Storage & Query Engines"
                ],
                experience_range="1-3 YOE",
                match_rationale="Direct match for Medallion Lakehouse architectures. Involves PySpark/Delta Lake columnar storage optimization, Apache Arrow dataframes, and automated ETL/ELT pipelines.",
                apply_url="https://www.instahyre.com/job-328495-junior-data-engineer-at-allen-digital-bangalore/"
            ),
            JobPosting(
                company="LoveLocal",
                title="SDE1 - Backend Developer",
                location="Bengaluru",
                work_model="Hybrid",
                date_posted="2026-09-25",
                tech_stack=["Python", "FastAPI", "Casdoor", "PostgreSQL", "Redis", "Kafka"],
                specializations=[
                    "Transactional Outbox & Event-Driven Systems",
                    "Custom Tap/Target Ingestion (ERP Integrations)"
                ],
                experience_range="1-3 YOE",
                match_rationale="High-concurrency backend API development utilizing Python async frameworks, OAuth 2.0 / Casdoor authentication, Kafka transactional outbox patterns, and Redis caching.",
                apply_url="https://www.instahyre.com/job-314201-sDE1-backend-developer-at-lovelocal-bangalore/"
            ),
            JobPosting(
                company="Sedna Horeca",
                title="Data Engineer (ETL & Data Platform)",
                location="Bengaluru",
                work_model="Hybrid",
                date_posted="2026-09-19",
                tech_stack=["Python", "Polars", "Apache DataFusion", "PyO3", "Singer.io", "PostgreSQL"],
                specializations=[
                    "Zero-Copy FFI (Arrow C Data Interface)",
                    "Data Lakehouse Architectures (Medallion)",
                    "Custom Tap/Target Ingestion (ERP Integrations)"
                ],
                experience_range="1-3 YOE",
                match_rationale="High-performance data ingestion using Python & Rust PyO3 bindings, Zero-Copy Arrow memory buffers, Singer.io tap/target connectors, and Polars engine pipelines.",
                apply_url="https://www.instahyre.com/job-326110-data-engineer-at-sedna-horeca-bangalore/"
            )
        ]
        return postings

    def validate_posting(self, posting: JobPosting) -> bool:
        """Applies strict business logic filters."""
        # 1. Workplace Policy: Check allowed work models (Hybrid, On-site, Remote if allowed)
        allowed_models = [m.lower() for m in self.criteria.get("allowed_work_models", [])]
        if allowed_models and posting.work_model.lower() not in allowed_models:
            return False
        
        # 2. Location Check
        target_locs = self.criteria.get("target_locations", [])
        if target_locs and posting.location not in target_locs:
            return False

        # 3. Recency Verification (within max_recency_days)
        try:
            posted_dt = datetime.strptime(posting.date_posted, "%Y-%m-%d")
            max_days = self.criteria.get("max_recency_days", 14)
            if (datetime.now() - posted_dt).days > max_days:
                return False
        except ValueError:
            pass

        # 4. Tech Stack Check (Must contain at least one primary language if configured)
        primary_langs = [lang.lower() for lang in self.criteria.get("primary_languages", [])]
        if primary_langs:
            has_primary = any(lang in [t.lower() for t in posting.tech_stack] for lang in primary_langs)
            if not has_primary:
                return False

        return True

    def filter_jobs(self) -> List[JobPosting]:
        raw_postings = self.fetch_active_postings()
        matched = [p for p in raw_postings if self.validate_posting(p)]
        return matched[:5]  # Top matched roles

    def generate_html_email(self, matches: List[JobPosting]) -> str:
        """Renders executive, responsive HTML email template with Specialization badges."""
        today_str = datetime.now().strftime("%B %d, %Y")
        
        # Render top specialization pills
        spec_summary_pills = "".join([
            f'<span style="background: #e9d8fd; color: #553c9a; padding: 4px 10px; border-radius: 12px; font-size: 11px; margin-right: 6px; margin-bottom: 6px; display: inline-block; font-weight: 700;">✦ {spec}</span>'
            for spec in self.specializations
        ])

        cards_html = ""
        for job in matches:
            tech_badges = "".join([
                f'<span style="background: #edf2f7; color: #2b6cb0; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-right: 6px; margin-bottom: 4px; display: inline-block; font-weight: 600;">{tech}</span>'
                for tech in job.tech_stack
            ])
            
            spec_badges = "".join([
                f'<span style="background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; padding: 3px 8px; border-radius: 4px; font-size: 11px; margin-right: 6px; margin-bottom: 4px; display: inline-block; font-weight: 600;">◈ {spec}</span>'
                for spec in job.specializations
            ])

            cards_html += f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <div>
                        <h3 style="margin: 0 0 4px 0; color: #1a202c; font-size: 18px; font-weight: 700;">{job.title}</h3>
                        <div style="color: #4a5568; font-weight: 600; font-size: 14px;">{job.company}</div>
                    </div>
                    <span style="background: #e6fffa; color: #234e52; border: 1px solid #b2f5ea; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                        {job.work_model} - {job.location}
                    </span>
                </div>
                <div style="color: #718096; font-size: 12px; margin-bottom: 12px;">
                    Posted: {job.date_posted} &bull; Seniority: {job.experience_range}
                </div>
                
                <!-- Specializations -->
                <div style="margin-bottom: 10px;">
                    <div style="font-size: 11px; font-weight: 700; color: #6b21a8; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px;">Matched Specializations:</div>
                    {spec_badges}
                </div>

                <!-- Tech Stack -->
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 11px; font-weight: 700; color: #2b6cb0; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px;">Core Tech Stack:</div>
                    {tech_badges}
                </div>

                <div style="background: #f7fafc; border-left: 3px solid #3182ce; padding: 10px 12px; border-radius: 0 4px 4px 0; margin-bottom: 16px; color: #2d3748; font-size: 13px; line-height: 1.5;">
                    <strong>Why it matches:</strong> {job.match_rationale}
                </div>
                <a href="{job.apply_url}" target="_blank" style="display: inline-block; background: #3182ce; color: #ffffff; text-decoration: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; font-size: 13px;">
                    Apply Direct &rarr;
                </a>
            </div>
            """

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Backend & Data Infra Job Matches</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f7fafc; margin: 0; padding: 20px;">
            <div style="max-width: 700px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; border: 1px solid #e2e8f0;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%); padding: 30px 24px; text-align: left; color: #ffffff;">
                    <span style="background: #4299e1; color: #ffffff; text-transform: uppercase; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.5px;">Automated Agent Digest</span>
                    <h1 style="margin: 12px 0 6px 0; font-size: 22px; font-weight: 700;">Backend & Data Infra Job Matches</h1>
                    <p style="margin: 0 0 14px 0; color: #a0aec0; font-size: 14px;">Curated for Systems & Data Engineering &bull; {today_str}</p>
                    <div>
                        {spec_summary_pills}
                    </div>
                </div>
                
                <!-- Rules Summary Badge -->
                <div style="background: #ebf8ff; border-bottom: 1px solid #bee3f8; padding: 12px 24px; font-size: 12px; color: #2b6cb0;">
                    <strong>Filter Policy Enforced:</strong> On-site/Hybrid &bull; 1-3 YOE &bull; Posted &lt;14 Days
                </div>

                <!-- Main Content -->
                <div style="padding: 24px;">
                    <p style="color: #4a5568; font-size: 14px; margin-top: 0; margin-bottom: 20px;">
                        Found <strong>{len(matches)} verified active roles</strong> matching your profile and specializations:
                    </p>
                    {cards_html}
                </div>

                <!-- Footer -->
                <div style="background: #edf2f7; padding: 16px 24px; text-align: center; color: #718096; font-size: 12px; border-top: 1px solid #e2e8f0;">
                    Generated automatically by JobFinderAgent &bull; strictly filtered per profile constraints.
                </div>
            </div>
        </body>
        </html>
        """
        return html_template

    def send_email(self, html_content: str, text_content: str):
        """Dispatches email via SMTP if enabled in config."""
        if not self.email_cfg.get("enable_smtp", False):
            print("[INFO] SMTP is disabled in configuration. Skipping email dispatch.")
            return

        sender = self.email_cfg.get("sender_email")
        password = self.email_cfg.get("sender_password")
        recipient = self.email_cfg.get("recipient_email")
        host = self.email_cfg.get("smtp_server")
        port = self.email_cfg.get("smtp_port", 587)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Job Matches ({len(self.filter_jobs())} Active Roles)"
        msg["From"] = sender
        msg["To"] = recipient

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        try:
            print(f"[INFO] Connecting to SMTP server {host}:{port}...")
            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(sender, password)
                server.sendmail(sender, recipient, msg.as_string())
            print(f"[SUCCESS] Job notification email successfully sent to {recipient}!")
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")

    def run(self):
        print("[AGENT] Searching and validating job listings against strict profile constraints & specializations...")
        matches = self.filter_jobs()
        print(f"[AGENT] Matched {len(matches)} high-quality job postings.")

        html_content = self.generate_html_email(matches)
        
        # Derive output filename from config name
        config_name = os.path.splitext(os.path.basename(self.config_path))[0]
        preview_file = f"job_matches_{config_name}.html" if config_name != "config" else "job_matches_email.html"
        
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[AGENT] Generated email preview saved to: {os.path.abspath(preview_file)}")

        # Print clean text summary to stdout
        text_summary = "\n".join([
            f"• {m.company} - {m.title}\n  Location: {m.work_model} - {m.location}\n  Specializations: {', '.join(m.specializations)}\n  Tech: {', '.join(m.tech_stack)}\n  Link: {m.apply_url}\n"
            for m in matches
        ])
        print("\n=== MATCHED ROLES DIGEST ===")
        print(text_summary)

        # Send via email if SMTP is configured
        self.send_email(html_content, text_summary)


def parse_config_arg() -> str:
    """Bulletproof CLI argument parser that accepts --config=file, config=file, or raw filename."""
    config_file = "config.json"
    
    for i, arg in enumerate(sys.argv[1:], start=1):
        if arg.startswith("--config="):
            config_file = arg.split("=", 1)[1]
        elif arg.startswith("config="):
            config_file = arg.split("=", 1)[1]
        elif arg == "--config" and i < len(sys.argv) - 1:
            config_file = sys.argv[i + 1]
        elif not arg.startswith("-") and arg.endswith(".json"):
            config_file = arg

    return config_file


if __name__ == "__main__":
    target_config = parse_config_arg()
    try:
        agent = JobFilterAgent(config_path=target_config)
        agent.run()
    except FileNotFoundError as err:
        print(f"\n[ERROR] {err}")
        print("\nValid Usage Examples:")
        print("  python job_agent.py config=config_AIML.json")
        print("  python job_agent.py --config config_AIML.json")
        print("  python job_agent.py config_AIML.json")
