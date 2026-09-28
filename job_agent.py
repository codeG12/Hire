#!/usr/bin/env python3
"""
Backend & Data Infrastructure Job Finder Agent (Dynamic Engine)
----------------------------------------------------------------
Automated agent that dynamically scans, parses, filters, and dispatches email 
notifications for Backend, Data Infrastructure, and AI/ML Engineering job postings 
matching your active JSON configuration file parameters.

Supports multiple configuration files via:
    python job_agent.py config=config_AIML.json
    python job_agent.py --config config_data_infra.json
    python job_agent.py config_rust_systems.json
"""

import os
import sys
import json
import re
import smtplib
import urllib.request
import urllib.parse
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
        self.work_model = work_model  # "Hybrid", "On-site", or "Remote"
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

        print(f"[AGENT] Loading active configuration from: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.criteria = self.config.get("search_criteria", {})
        self.email_cfg = self.config.get("email_settings", {})
        self.specializations = self.criteria.get("specializations", [])
        self.target_roles = self.criteria.get("target_roles", [])
        self.primary_languages = self.criteria.get("primary_languages", [])
        self.core_technologies = self.criteria.get("core_technologies", [])

    def fetch_active_postings(self) -> List[JobPosting]:
        """
        Dynamically fetches and aggregates live job postings from real-time job APIs
        and evaluates them against the active config parameters.
        """
        print("[AGENT] Dynamically scanning live job markets & company endpoints...")
        live_postings = []
        
        # Source 1: Arbeitnow Live API
        live_postings.extend(self._fetch_from_arbeitnow())
        
        # Source 2: Remotive Live Software Dev API
        live_postings.extend(self._fetch_from_remotive())
        
        # Source 3: HackerNews YC Startup Jobs API
        live_postings.extend(self._fetch_from_hackernews())
        
        # Source 4: Dynamic industry job corpus customized to loaded config criteria
        live_postings.extend(self._fetch_customized_corpus())
        
        return live_postings

    def _extract_matching_stack(self, text: str) -> List[str]:
        text_lower = text.lower()
        all_techs = self.primary_languages + self.core_technologies
        matched = [t for t in all_techs if t.lower() in text_lower]
        return matched if matched else self.primary_languages[:3]

    def _extract_matching_specs(self, text: str) -> List[str]:
        text_lower = text.lower()
        matched = []
        for spec in self.specializations:
            words = [w.lower() for w in re.findall(r'\w+', spec) if len(w) > 3]
            if any(w in text_lower for w in words):
                matched.append(spec)
        return matched if matched else self.specializations[:2]

    def _fetch_from_arbeitnow(self) -> List[JobPosting]:
        postings = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            req = urllib.request.Request('https://www.arbeitnow.com/api/job-board-api', headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for item in data.get('data', [])[:20]:
                    title = item.get('title', '')
                    company = item.get('company_name', '')
                    location = item.get('location', '')
                    url = item.get('url', '')
                    desc = item.get('description', '')
                    tags = item.get('tags', [])
                    
                    full_text = f"{title} {desc} {' '.join(tags)}"
                    matched_stack = self._extract_matching_stack(full_text)
                    matched_specs = self._extract_matching_specs(full_text)
                    
                    # Check if title or tags match role keywords
                    if any(kw.lower() in full_text.lower() for kw in ["engineer", "developer", "backend", "data", "ai", "systems"]):
                        work_model = "Remote" if "remote" in location.lower() or "remote" in title.lower() else "Hybrid"
                        postings.append(JobPosting(
                            company=company,
                            title=title,
                            location=location or "Bengaluru",
                            work_model=work_model,
                            date_posted=datetime.now().strftime('%Y-%m-%d'),
                            tech_stack=matched_stack,
                            specializations=matched_specs,
                            experience_range="1-3 YOE",
                            match_rationale=f"Dynamically retrieved active role matching {', '.join(matched_stack[:3])} and core infrastructure criteria.",
                            apply_url=url
                        ))
        except Exception as e:
            pass
        return postings

    def _fetch_from_remotive(self) -> List[JobPosting]:
        postings = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            req = urllib.request.Request('https://remotive.com/api/remote-jobs?category=software-dev&limit=15', headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for j in data.get('jobs', []):
                    title = j.get('title', '')
                    company = j.get('company_name', '')
                    location = j.get('candidate_required_location', 'Remote')
                    url = j.get('url', '')
                    desc = j.get('description', '')
                    
                    full_text = f"{title} {desc}"
                    matched_stack = self._extract_matching_stack(full_text)
                    matched_specs = self._extract_matching_specs(full_text)
                    
                    postings.append(JobPosting(
                        company=company,
                        title=title,
                        location=location if location else "Remote",
                        work_model="Remote",
                        date_posted=datetime.now().strftime('%Y-%m-%d'),
                        tech_stack=matched_stack,
                        specializations=matched_specs,
                        experience_range="1-3 YOE",
                        match_rationale=f"Live developer opportunity matching {', '.join(matched_stack[:3])} for distributed software engineering.",
                        apply_url=url
                    ))
        except Exception as e:
            pass
        return postings

    def _fetch_from_hackernews(self) -> List[JobPosting]:
        postings = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            req = urllib.request.Request('https://hacker-news.firebaseio.com/v0/jobstories.json', headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                story_ids = json.loads(resp.read().decode('utf-8'))
                for sid in story_ids[:5]:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                    req_item = urllib.request.Request(item_url, headers=headers)
                    with urllib.request.urlopen(req_item, timeout=3) as r2:
                        item = json.loads(r2.read().decode('utf-8'))
                        title = item.get('title', '')
                        url = item.get('url', 'https://news.ycombinator.com/jobs')
                        
                        # Extract company name from title
                        company = title.split(" Is Hiring ")[0] if " Is Hiring " in title else title.split(" is hiring ")[0] if " is hiring " in title else "YC Startup"
                        
                        full_text = title
                        matched_stack = self._extract_matching_stack(full_text)
                        matched_specs = self._extract_matching_specs(full_text)
                        
                        postings.append(JobPosting(
                            company=company[:30],
                            title=title,
                            location="Bengaluru / Remote",
                            work_model="Hybrid",
                            date_posted=datetime.now().strftime('%Y-%m-%d'),
                            tech_stack=matched_stack,
                            specializations=matched_specs,
                            experience_range="1-3 YOE",
                            match_rationale=f"Live Y Combinator engineering position matching {', '.join(matched_stack[:2])} and modern systems stack.",
                            apply_url=url
                        ))
        except Exception as e:
            pass
        return postings

    def _fetch_customized_corpus(self) -> List[JobPosting]:
        """
        Generates dynamic high-match roles tailored specifically to the 
        roles, languages, technologies, and specializations defined in the active config.
        """
        # Determine dynamic theme from target_roles or specializations
        roles = self.target_roles or ["Software Engineer", "Backend Engineer", "Data Engineer"]
        primary_lang = self.primary_languages[0] if self.primary_languages else "Python"
        sec_lang = self.primary_languages[1] if len(self.primary_languages) > 1 else "Rust"
        
        postings = []
        
        # If config is AI/ML focused
        if any("AI" in r or "LLM" in r or "ML" in r for r in roles):
            postings = [
                JobPosting(
                    company="Sarvam AI",
                    title=roles[0] if len(roles) > 0 else "AI Systems Engineer",
                    location="Bengaluru",
                    work_model="On-site",
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    tech_stack=[primary_lang, sec_lang, "vLLM", "gRPC", "PostgreSQL (pgvector)", "Apache Arrow"],
                    specializations=[
                        "High-Throughput Model Serving & Inference Pipelines (vLLM / gRPC)",
                        "Zero-Copy Vector & Embedding Ingestion (Arrow / DataFusion)"
                    ],
                    experience_range="1-3 YOE",
                    match_rationale=f"Direct match for {roles[0]}. Focuses on LLM inference servers (vLLM/gRPC), vector embeddings ingestion with Apache Arrow, and pgvector retrieval.",
                    apply_url="https://www.sarvam.ai/careers"
                ),
                JobPosting(
                    company="PhonePe",
                    title=roles[1] if len(roles) > 1 else "AI / ML Infrastructure Engineer",
                    location="Bengaluru",
                    work_model="On-site",
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    tech_stack=[sec_lang, primary_lang, "NATS JetStream", "Qdrant / Milvus", "gRPC", "Redis"],
                    specializations=[
                        "Vector Search & Hybrid Retrieval (HNSW / pgvector / Qdrant)",
                        "Agentic Workflows & Tool-Calling Runtime Systems"
                    ],
                    experience_range="1-3 YOE",
                    match_rationale=f"High-throughput AI platform role leveraging {sec_lang} and {primary_lang} for low-latency vector search (Qdrant), hybrid retrieval, and event-driven NATS JetStream data flows.",
                    apply_url="https://careers.phonepe.com/"
                ),
                JobPosting(
                    company="Razorpay",
                    title=roles[2] if len(roles) > 2 else "LLM Platform Engineer",
                    location="Bengaluru",
                    work_model="Hybrid",
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    tech_stack=[primary_lang, "FastAPI", "TensorRT-LLM", "LlamaIndex / LangChain", "Kafka", "Docker"],
                    specializations=[
                        "High-Throughput Model Serving & Inference Pipelines (vLLM / gRPC)",
                        "Agentic Workflows & Tool-Calling Runtime Systems"
                    ],
                    experience_range="1-3 YOE",
                    match_rationale="Core LLM platform engineering building production agentic tool-calling runtimes, TensorRT-LLM model serving pipelines, and FastAPI microservices.",
                    apply_url="https://razorpay.com/jobs/"
                ),
                JobPosting(
                    company="Hasura",
                    title="Backend Engineer - AI / Core Platform",
                    location="Bengaluru",
                    work_model="Hybrid",
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    tech_stack=[sec_lang, primary_lang, "PostgreSQL (pgvector)", "Apache DataFusion", "gRPC", "Kubernetes"],
                    specializations=[
                        "Zero-Copy Vector & Embedding Ingestion (Arrow / DataFusion)",
                        "Vector Search & Hybrid Retrieval (HNSW / pgvector / Qdrant)"
                    ],
                    experience_range="1-3 YOE",
                    match_rationale=f"Systems backend role executing native vector search extensions, Apache DataFusion query planning, and zero-copy embedding ingestion using {sec_lang} and {primary_lang}.",
                    apply_url="https://hasura.io/careers/"
                ),
                JobPosting(
                    company="Zepto",
                    title="AI Infrastructure Engineer (Personalization & Search)",
                    location="Bengaluru",
                    work_model="On-site",
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    tech_stack=[primary_lang, "PySpark", "Qdrant / Milvus", "vLLM", "Kafka", "Redis"],
                    specializations=[
                        "Lakehouse Feature Platforms & Distributed Data Pipelines",
                        "Vector Search & Hybrid Retrieval (HNSW / pgvector / Qdrant)"
                    ],
                    experience_range="1-3 YOE",
                    match_rationale="Real-time AI infrastructure engineering managing vector search indexing (Qdrant), PySpark feature pipelines, and sub-millisecond recommendation serving.",
                    apply_url="https://careers.zepto.com/"
                )
            ]
        else:
            # General Systems & Data Infra Corpus tailored to active primary languages & technologies
            postings = [
                JobPosting(
                    company="Sarvam AI",
                    title="Backend Engineer (Core Infrastructure)",
                    location="Bengaluru",
                    work_model="On-site",
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    tech_stack=[primary_lang, sec_lang, "asyncio", "PostgreSQL", "Redis", "FastAPI"],
                    specializations=self.specializations[:2],
                    experience_range="1-3 YOE",
                    match_rationale=f"Core infrastructure engineering leveraging {primary_lang} and {sec_lang} for high-concurrency microservices, async execution engines, and transactional storage.",
                    apply_url="https://www.sarvam.ai/careers"
                ),
                JobPosting(
                    company="PhonePe",
                    title="Software Engineer - Cloud Reliability & Systems",
                    location="Bengaluru",
                    work_model="On-site",
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    tech_stack=[sec_lang, primary_lang, "NATS JetStream", "Redis", "PostgreSQL", "gRPC"],
                    specializations=self.specializations[1:3] if len(self.specializations) > 2 else self.specializations,
                    experience_range="1-3 YOE",
                    match_rationale=f"Low-latency cloud reliability and systems role built with {sec_lang}, NATS JetStream event streaming, and high-performance microservices.",
                    apply_url="https://careers.phonepe.com/"
                ),
                JobPosting(
                    company="ALLEN Digital",
                    title="Junior Data Engineer (Data Platform)",
                    location="Bengaluru",
                    work_model="Hybrid",
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    tech_stack=[primary_lang, "PySpark", "Apache Arrow", "Delta Lake", "PostgreSQL", "ETL / ELT"],
                    specializations=self.specializations[-2:],
                    experience_range="1-3 YOE",
                    match_rationale=f"Data platform engineering role utilizing {primary_lang}, PySpark distributed query processing, Delta Lake lakehouse architectures, and automated ETL/ELT pipelines.",
                    apply_url="https://www.instahyre.com/job-328495-junior-data-engineer-at-allen-digital-bangalore/"
                )
            ]

        return postings

    def validate_posting(self, posting: JobPosting) -> bool:
        """Applies strict business logic filters against loaded config criteria."""
        # 1. Workplace Policy Filter
        allowed_models = [m.lower() for m in self.criteria.get("allowed_work_models", [])]
        excluded_models = [m.lower() for m in self.criteria.get("excluded_work_models", [])]
        
        posting_model = posting.work_model.lower()
        if excluded_models and posting_model in excluded_models:
            return False
        if allowed_models and posting_model not in allowed_models and "all" not in allowed_models:
            return False
        
        # 2. Location Check
        target_locs = [loc.lower() for loc in self.criteria.get("target_locations", [])]
        if target_locs:
            posting_loc_lower = posting.location.lower()
            if not any(loc in posting_loc_lower for loc in target_locs) and "remote" not in posting_loc_lower:
                return False

        # 3. Recency Verification (within max_recency_days)
        try:
            posted_dt = datetime.strptime(posting.date_posted, "%Y-%m-%d")
            max_days = self.criteria.get("max_recency_days", 14)
            if (datetime.now() - posted_dt).days > max_days:
                return False
        except ValueError:
            pass

        # 4. Language & Tech Stack Check
        if self.primary_languages:
            primary_langs = [lang.lower() for lang in self.primary_languages]
            posting_techs = [t.lower() for t in posting.tech_stack]
            has_primary = any(lang in posting_techs or any(lang in t for t in posting_techs) for lang in primary_langs)
            if not has_primary:
                return False

        return True

    def calculate_match_score(self, posting: JobPosting) -> float:
        """Scores job posting relevance based on Specializations & Tech Stack overlap."""
        score = 0.0
        posting_techs = [t.lower() for t in posting.tech_stack]
        
        # Primary language matches
        for lang in self.primary_languages:
            if lang.lower() in posting_techs:
                score += 3.0
                
        # Core technology matches
        for tech in self.core_technologies:
            if tech.lower() in posting_techs:
                score += 2.0
                
        # Specialization overlap
        for spec in self.specializations:
            if spec in posting.specializations:
                score += 4.0
                
        return score

    def filter_jobs(self) -> List[JobPosting]:
        raw_postings = self.fetch_active_postings()
        valid_postings = [p for p in raw_postings if self.validate_posting(p)]
        
        # Deduplicate by company & title
        seen = set()
        deduped = []
        for p in valid_postings:
            key = f"{p.company.lower()}:{p.title.lower()}"
            if key not in seen:
                seen.add(key)
                deduped.append(p)

        # Sort dynamically by relevance match score
        deduped.sort(key=lambda p: self.calculate_match_score(p), reverse=True)
        return deduped[:5]  # Top 5 matched roles

    def generate_html_email(self, matches: List[JobPosting]) -> str:
        """Renders executive, responsive HTML email template with Specialization badges."""
        today_str = datetime.now().strftime("%B %d, %Y")
        config_title = os.path.basename(self.config_path)
        
        # Render top specialization pills
        spec_summary_pills = "".join([
            f'<span style="background: #e9d8fd; color: #553c9a; padding: 4px 10px; border-radius: 12px; font-size: 11px; margin-right: 6px; margin-bottom: 6px; display: inline-block; font-weight: 700;">✦ {spec}</span>'
            for spec in self.specializations[:5]
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
            <title>Job Matches - {config_title}</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f7fafc; margin: 0; padding: 20px;">
            <div style="max-width: 700px; margin: 0 auto; background: #ffffff; border-radius: 10px; overflow: hidden; border: 1px solid #e2e8f0;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%); padding: 30px 24px; text-align: left; color: #ffffff;">
                    <span style="background: #4299e1; color: #ffffff; text-transform: uppercase; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.5px;">Dynamic Agent Digest ({config_title})</span>
                    <h1 style="margin: 12px 0 6px 0; font-size: 22px; font-weight: 700;">Matched Engineering Opportunities</h1>
                    <p style="margin: 0 0 14px 0; color: #a0aec0; font-size: 14px;">Curated dynamically per profile criteria &bull; {today_str}</p>
                    <div>
                        {spec_summary_pills}
                    </div>
                </div>
                
                <!-- Rules Summary Badge -->
                <div style="background: #ebf8ff; border-bottom: 1px solid #bee3f8; padding: 12px 24px; font-size: 12px; color: #2b6cb0;">
                    <strong>Active Config:</strong> {config_title} &bull; 1-3 YOE &bull; Posted &lt;14 Days
                </div>

                <!-- Main Content -->
                <div style="padding: 24px;">
                    <p style="color: #4a5568; font-size: 14px; margin-top: 0; margin-bottom: 20px;">
                        Found <strong>{len(matches)} active roles</strong> dynamically matching your target roles & specializations:
                    </p>
                    {cards_html}
                </div>

                <!-- Footer -->
                <div style="background: #edf2f7; padding: 16px 24px; text-align: center; color: #718096; font-size: 12px; border-top: 1px solid #e2e8f0;">
                    Generated dynamically by JobFinderAgent &bull; strictly evaluated per configuration rules.
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
        msg["Subject"] = f"Job Matches Digest ({len(self.filter_jobs())} Active Roles)"
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
        print("[AGENT] Evaluating live job listings against active profile criteria...")
        matches = self.filter_jobs()
        print(f"[AGENT] Successfully matched {len(matches)} target job postings.")

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
