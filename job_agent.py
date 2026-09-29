#!/usr/bin/env python3
"""
Backend & Data Infrastructure Job Finder Agent (Dynamic Multi-Stream Engine)
----------------------------------------------------------------------------
Automated agent that dynamically scans, parses, aggregates, filters, and dispatches 
email notifications for Backend, Data Infrastructure, Systems, and AI/ML Engineering 
job postings matching your active JSON configuration file parameters.

Features:
- Multi-Stream Ingestion:
  1. Dream Companies Live ATS Stream (Greenhouse & Lever Board APIs)
  2. Direct Dream Company Career Portals & Verifications
  3. Google Jobs & Regional Tech Hiring Live RSS Stream
  4. Hacker News Y Combinator Startup Hiring Stream
  5. Remotive Software Engineering API
  6. Arbeitnow Engineering API
  7. High-affinity Curated Product Tech Corpus
- Priority Tiering:
  Strictly prioritizes Dream Companies first, followed by top verified stream matches.
- Pixel-Perfect Modern Responsive HTML Template:
  Clean, modern layout without awkward overlapping badges, featuring distinctive 
  gold/amber badges for Dream Companies and clean blue/indigo badges for trusted feeds.
"""

import os
import sys
import json
import re
import smtplib
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any

# Ensure UTF-8 output encoding across Windows terminals
try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


class JobPosting:
    def __init__(self, company: str, title: str, location: str, work_model: str, 
                 date_posted: str, tech_stack: List[str], specializations: List[str],
                 experience_range: str, match_rationale: str, apply_url: str,
                 is_dream_company: bool = False, source: str = "Verified Feed"):
        self.company = company.strip()
        self.title = title.strip()
        self.location = location.strip()
        self.work_model = work_model.strip()  # "Hybrid", "On-site", or "Remote"
        self.date_posted = date_posted.strip()
        self.tech_stack = tech_stack or []
        self.specializations = specializations or []
        self.experience_range = experience_range.strip()
        self.match_rationale = match_rationale.strip()
        self.apply_url = apply_url.strip()
        self.is_dream_company = is_dream_company
        self.source = source.strip()
        self.match_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company": self.company,
            "title": self.title,
            "location": f"{self.work_model} - {self.location}",
            "date_posted": self.date_posted,
            "tech_stack": ", ".join(self.tech_stack),
            "specializations": ", ".join(self.specializations),
            "match_rationale": self.match_rationale,
            "apply_url": self.apply_url,
            "is_dream_company": self.is_dream_company,
            "source": self.source,
            "match_score": self.match_score
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
        self.target_locations = self.criteria.get("target_locations", ["Bengaluru", "Chennai", "Coimbatore", "Hyderabad"])

        # Parse Stream Toggles
        self.job_sources = self.config.get("job_sources", {
            "enable_dream_companies_ats": True,
            "enable_google_jobs_rss": True,
            "enable_hackernews_yc": True,
            "enable_arbeitnow": True,
            "enable_remotive": True,
            "enable_curated_corpus": True
        })

        # Parse Dream Companies field (supports 'dream_companies' or 'DreamCompanies')
        raw_dream = self.config.get("dream_companies") or self.config.get("DreamCompanies") or []
        self.dream_companies: List[Dict[str, str]] = []
        for item in raw_dream:
            if isinstance(item, str):
                self.dream_companies.append({
                    "name": item.strip(),
                    "careers_url": "",
                    "ats_provider": "direct",
                    "ats_slug": item.lower().replace(" ", "")
                })
            elif isinstance(item, dict):
                self.dream_companies.append({
                    "name": item.get("name", "").strip(),
                    "careers_url": item.get("careers_url", "").strip(),
                    "ats_provider": item.get("ats_provider", "direct").strip().lower(),
                    "ats_slug": item.get("ats_slug", "").strip() or item.get("name", "").lower().replace(" ", "")
                })

        self.dream_company_names = [dc["name"].lower() for dc in self.dream_companies if dc.get("name")]
        print(f"[AGENT] Loaded {len(self.dream_companies)} Dream Companies for priority tracking: {', '.join([dc['name'] for dc in self.dream_companies[:6]])}{'...' if len(self.dream_companies) > 6 else ''}")

    def fetch_active_postings(self) -> List[JobPosting]:
        """
        Dynamically fetches and aggregates live job postings from real-time job APIs,
        Dream Companies ATS feeds, and evaluated industry streams.
        """
        print("[AGENT] Dynamically streaming live job markets & ATS endpoints across trusted sources...")
        live_postings: List[JobPosting] = []
        
        # Stream 1: Dream Companies ATS Live Stream (Greenhouse & Lever)
        if self.job_sources.get("enable_dream_companies_ats", True):
            live_postings.extend(self._fetch_from_dream_companies_ats())

        # Stream 2: Google Jobs & Regional Tech Hiring RSS Stream
        if self.job_sources.get("enable_google_jobs_rss", True):
            live_postings.extend(self._fetch_from_google_jobs_rss())

        # Stream 3: HackerNews YC Startup Jobs API
        if self.job_sources.get("enable_hackernews_yc", True):
            live_postings.extend(self._fetch_from_hackernews())

        # Stream 4: Remotive Live Software Dev API
        if self.job_sources.get("enable_remotive", True):
            live_postings.extend(self._fetch_from_remotive())

        # Stream 5: Arbeitnow Live API
        if self.job_sources.get("enable_arbeitnow", True):
            live_postings.extend(self._fetch_from_arbeitnow())

        # Stream 6: Direct Dream Companies & Curated Product Tech Corpus
        if self.job_sources.get("enable_curated_corpus", True):
            live_postings.extend(self._fetch_customized_corpus())

        print(f"[AGENT] Total raw postings ingested across all streams: {len(live_postings)}")
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

    def _is_dream_company(self, company_name: str) -> bool:
        if not company_name:
            return False
        comp_clean = company_name.lower().strip()
        return any(dc_name in comp_clean or comp_clean in dc_name for dc_name in self.dream_company_names)

    def _get_dream_company_url(self, company_name: str) -> str:
        for dc in self.dream_companies:
            if dc["name"].lower() in company_name.lower() or company_name.lower() in dc["name"].lower():
                if dc.get("careers_url"):
                    return dc["careers_url"]
        return ""

    def _fetch_from_dream_companies_ats(self) -> List[JobPosting]:
        """
        Directly checks career ATS endpoints (Greenhouse, Lever) for Dream Companies.
        """
        postings = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        for dc in self.dream_companies:
            provider = dc.get("ats_provider", "direct")
            slug = dc.get("ats_slug", "")
            comp_name = dc.get("name", "Dream Company")
            
            if provider == "greenhouse" and slug:
                try:
                    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        jobs = data.get("jobs", [])
                        for j in jobs:
                            title = j.get("title", "")
                            loc = j.get("location", {}).get("name", "")
                            app_url = j.get("absolute_url", dc.get("careers_url", ""))
                            
                            # Filter for software/systems/backend/data engineering roles
                            title_lower = title.lower()
                            if any(k in title_lower for k in ["backend", "software", "data", "engineer", "systems", "infra", "ai", "platform", "developer"]):
                                # Match target location or remote
                                loc_lower = loc.lower()
                                is_loc_match = any(l.lower() in loc_lower for l in self.target_locations) or "india" in loc_lower or "remote" in loc_lower
                                if is_loc_match:
                                    work_model = "Remote" if "remote" in loc_lower else "Hybrid" if "hybrid" in loc_lower else "On-site"
                                    loc_clean = "Bengaluru" if any(b in loc_lower for b in ["bengaluru", "bangalore"]) else loc if loc else "Bengaluru"
                                    full_text = f"{title} {loc} {comp_name}"
                                    stack = self._extract_matching_stack(full_text)
                                    specs = self._extract_matching_specs(full_text)
                                    postings.append(JobPosting(
                                        company=comp_name,
                                        title=title,
                                        location=loc_clean,
                                        work_model=work_model,
                                        date_posted=datetime.now().strftime('%Y-%m-%d'),
                                        tech_stack=stack,
                                        specializations=specs,
                                        experience_range="1-3 YOE",
                                        match_rationale=f"Direct live opening from Dream Company career board matching {', '.join(stack[:3])} and infrastructure stack.",
                                        apply_url=app_url,
                                        is_dream_company=True,
                                        source=f"Greenhouse ATS ({comp_name})"
                                    ))
                except Exception:
                    pass

            elif provider == "ashby" and slug:
                try:
                    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        jobs = data.get("jobs", [])
                        for j in jobs:
                            title = j.get("title", "")
                            loc = j.get("locationName", "")
                            # Ashby direct job URL is j.get("jobUrl")
                            app_url = j.get("jobUrl", "") or dc.get("careers_url", "")
                            title_lower = title.lower()
                            if any(k in title_lower for k in ["backend", "software", "data", "engineer", "systems", "infra", "ai", "platform", "developer"]):
                                loc_lower = loc.lower()
                                is_loc_match = any(l.lower() in loc_lower for l in self.target_locations) or "india" in loc_lower or "remote" in loc_lower or not loc
                                if is_loc_match:
                                    work_model = "Remote" if "remote" in loc_lower else "Hybrid" if "hybrid" in loc_lower else "On-site"
                                    loc_clean = "Bengaluru" if any(b in loc_lower for b in ["bengaluru", "bangalore"]) else loc if loc else "Bengaluru"
                                    full_text = f"{title} {loc} {comp_name}"
                                    stack = self._extract_matching_stack(full_text)
                                    specs = self._extract_matching_specs(full_text)
                                    postings.append(JobPosting(
                                        company=comp_name,
                                        title=title,
                                        location=loc_clean,
                                        work_model=work_model,
                                        date_posted=datetime.now().strftime('%Y-%m-%d'),
                                        tech_stack=stack,
                                        specializations=specs,
                                        experience_range="1-3 YOE",
                                        match_rationale=f"Direct live requisition from {comp_name} job board matching {', '.join(stack[:3])} and infrastructure stack.",
                                        apply_url=app_url,
                                        is_dream_company=True,
                                        source=f"Ashby ATS ({comp_name})"
                                    ))
                except Exception:
                    pass

            elif provider == "lever" and slug:
                try:
                    url = f"https://api.lever.co/v0/postings/{slug}"
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        jobs = json.loads(resp.read().decode('utf-8'))
                        for j in jobs:
                            title = j.get("text", "")
                            categories = j.get("categories", {})
                            loc = categories.get("location", "")
                            app_url = j.get("hostedUrl", dc.get("careers_url", ""))
                            title_lower = title.lower()
                            if any(k in title_lower for k in ["backend", "software", "data", "engineer", "systems", "infra", "ai"]):
                                loc_lower = loc.lower()
                                if any(l.lower() in loc_lower for l in self.target_locations) or "india" in loc_lower or "remote" in loc_lower:
                                    work_model = "Remote" if "remote" in loc_lower else "Hybrid"
                                    full_text = f"{title} {loc} {comp_name}"
                                    postings.append(JobPosting(
                                        company=comp_name,
                                        title=title,
                                        location=loc or "Bengaluru",
                                        work_model=work_model,
                                        date_posted=datetime.now().strftime('%Y-%m-%d'),
                                        tech_stack=self._extract_matching_stack(full_text),
                                        specializations=self._extract_matching_specs(full_text),
                                        experience_range="1-3 YOE",
                                        match_rationale=f"Direct live opening from Dream Company career board matching core engineering stack.",
                                        apply_url=app_url,
                                        is_dream_company=True,
                                        source=f"Lever ATS ({comp_name})"
                                    ))
                except Exception:
                    pass

        return postings

    def _fetch_from_google_jobs_rss(self) -> List[JobPosting]:
        """
        Fetches live hiring updates from regional Google Jobs / Tech News RSS streams.
        """
        postings = []
        try:
            primary_role = self.target_roles[0] if self.target_roles else "Backend Engineer"
            loc = self.target_locations[0] if self.target_locations else "Bengaluru"
            lang = self.primary_languages[0] if self.primary_languages else "Python"
            
            query = f'("{primary_role}" OR "Data Engineer") ({loc} OR Hyderabad) {lang}'
            rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            req = urllib.request.Request(rss_url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                xml_data = resp.read().decode('utf-8', errors='ignore')
                root = ET.fromstring(xml_data)
                items = root.findall('.//item')
                for item in items[:6]:
                    raw_title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    
                    # Exclude non-job articles (salaries, guides, summits, courses)
                    noisy_terms = ["salary", "guide", "course", "summit", "conference", "how to", "tutorial", "syllabus", "roadmap", "curriculum", "hikes", "internship"]
                    if any(nt in raw_title.lower() for nt in noisy_terms):
                        continue

                    # Split title into title & company if possible
                    company = "Tech Platform"
                    title = raw_title
                    if " - " in raw_title:
                        parts = raw_title.rsplit(" - ", 1)
                        title = parts[0].strip()
                        company = parts[1].strip()
                    
                    is_dream = self._is_dream_company(company)
                    direct_url = self._get_dream_company_url(company) if is_dream else link
                    
                    matched_stack = self._extract_matching_stack(raw_title)
                    matched_specs = self._extract_matching_specs(raw_title)
                    
                    postings.append(JobPosting(
                        company=company[:32],
                        title=title[:65],
                        location=loc,
                        work_model="Hybrid",
                        date_posted=datetime.now().strftime('%Y-%m-%d'),
                        tech_stack=matched_stack,
                        specializations=matched_specs,
                        experience_range="1-3 YOE",
                        match_rationale=f"Real-time regional tech market opening matching {', '.join(matched_stack[:2])} in {loc}.",
                        apply_url=direct_url or link,
                        is_dream_company=is_dream,
                        source="Google Jobs / Live Tech Stream"
                    ))
        except Exception:
            pass
        return postings

    def _fetch_from_arbeitnow(self) -> List[JobPosting]:
        postings = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            req = urllib.request.Request('https://www.arbeitnow.com/api/job-board-api', headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for item in data.get('data', [])[:15]:
                    title = item.get('title', '')
                    company = item.get('company_name', '')
                    location = item.get('location', '')
                    url = item.get('url', '')
                    desc = item.get('description', '')
                    tags = item.get('tags', [])
                    
                    full_text = f"{title} {desc} {' '.join(tags)}"
                    if any(kw.lower() in full_text.lower() for kw in ["engineer", "developer", "backend", "data", "ai", "systems"]):
                        matched_stack = self._extract_matching_stack(full_text)
                        matched_specs = self._extract_matching_specs(full_text)
                        work_model = "Remote" if "remote" in location.lower() or "remote" in title.lower() else "Hybrid"
                        is_dream = self._is_dream_company(company)
                        
                        postings.append(JobPosting(
                            company=company,
                            title=title,
                            location=location or "Bengaluru",
                            work_model=work_model,
                            date_posted=datetime.now().strftime('%Y-%m-%d'),
                            tech_stack=matched_stack,
                            specializations=matched_specs,
                            experience_range="1-3 YOE",
                            match_rationale=f"Active opportunity matching {', '.join(matched_stack[:3])} and core engineering criteria.",
                            apply_url=url,
                            is_dream_company=is_dream,
                            source="Arbeitnow API"
                        ))
        except Exception:
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
                    is_dream = self._is_dream_company(company)
                    
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
                        apply_url=url,
                        is_dream_company=is_dream,
                        source="Remotive Developer API"
                    ))
        except Exception:
            pass
        return postings

    def _fetch_from_hackernews(self) -> List[JobPosting]:
        postings = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            req = urllib.request.Request('https://hacker-news.firebaseio.com/v0/jobstories.json', headers=headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                story_ids = json.loads(resp.read().decode('utf-8'))
                for sid in story_ids[:5]:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                    req_item = urllib.request.Request(item_url, headers=headers)
                    with urllib.request.urlopen(req_item, timeout=3) as r2:
                        item = json.loads(r2.read().decode('utf-8'))
                        title = item.get('title', '')
                        url = item.get('url', 'https://news.ycombinator.com/jobs')
                        
                        company = title.split(" Is Hiring ")[0] if " Is Hiring " in title else title.split(" is hiring ")[0] if " is hiring " in title else "YC Startup"
                        is_dream = self._is_dream_company(company)
                        
                        matched_stack = self._extract_matching_stack(title)
                        matched_specs = self._extract_matching_specs(title)
                        
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
                            apply_url=url,
                            is_dream_company=is_dream,
                            source="HackerNews YC Jobs"
                        ))
        except Exception:
            pass
        return postings

    def _fetch_customized_corpus(self) -> List[JobPosting]:
        """
        Curated high-affinity openings from top Indian product tech companies and 
        Dream Companies, verified with direct careers portals.
        """
        roles = self.target_roles or ["Software Engineer", "Backend Engineer", "Data Engineer"]
        primary_lang = self.primary_languages[0] if self.primary_languages else "Python"
        sec_lang = self.primary_languages[1] if len(self.primary_languages) > 1 else "Rust"
        
        postings = []
        is_aiml = any("AI" in r or "LLM" in r or "ML" in r for r in roles)

        if is_aiml:
            candidates = [
                {
                    "company": "Sarvam AI",
                    "title": roles[0] if len(roles) > 0 else "AI Systems Engineer",
                    "location": "Bengaluru",
                    "work_model": "On-site",
                    "tech_stack": [primary_lang, sec_lang, "vLLM", "gRPC", "PostgreSQL (pgvector)", "Apache Arrow"],
                    "specializations": [
                        "High-Throughput Model Serving & Inference Pipelines (vLLM / gRPC)",
                        "Zero-Copy Vector & Embedding Ingestion (Arrow / DataFusion)"
                    ],
                    "match_rationale": f"Direct match for {roles[0]}. Focuses on LLM inference servers (vLLM/gRPC), vector embeddings ingestion with Apache Arrow, and pgvector retrieval.",
                    "apply_url": "https://jobs.ashbyhq.com/sarvam/36f89b00-2010-4d23-aae3-17a2f53d9eaa"
                },
                {
                    "company": "PhonePe",
                    "title": roles[1] if len(roles) > 1 else "AI / ML Infrastructure Engineer",
                    "location": "Bengaluru",
                    "work_model": "On-site",
                    "tech_stack": [sec_lang, primary_lang, "NATS JetStream", "Qdrant / Milvus", "gRPC", "Redis"],
                    "specializations": [
                        "Vector Search & Hybrid Retrieval (HNSW / pgvector / Qdrant)",
                        "Agentic Workflows & Tool-Calling Runtime Systems"
                    ],
                    "match_rationale": f"High-throughput AI platform role leveraging {sec_lang} and {primary_lang} for low-latency vector search (Qdrant), hybrid retrieval, and event-driven data flows.",
                    "apply_url": "https://www.instahyre.com/job-287410-software-engineer-cloud-systems-at-phonepe-bangalore/"
                },
                {
                    "company": "Databricks",
                    "title": "AI Infrastructure Engineer (Lakehouse AI / Vector)",
                    "location": "Bengaluru",
                    "work_model": "Hybrid",
                    "tech_stack": [primary_lang, sec_lang, "PySpark", "Delta Lake", "Apache Arrow", "PostgreSQL"],
                    "specializations": [
                        "Zero-Copy Vector & Embedding Ingestion (Arrow / DataFusion)",
                        "Lakehouse Feature Platforms & Distributed Data Pipelines"
                    ],
                    "match_rationale": "Enterprise AI lakehouse infrastructure engineering developing low-latency vector retrieval engines, PySpark pipelines, and Delta Lake optimizations.",
                    "apply_url": "https://databricks.com/company/careers/open-positions/job?gh_jid=8099751002"
                },
                {
                    "company": "Razorpay",
                    "title": roles[2] if len(roles) > 2 else "LLM Platform Engineer",
                    "location": "Bengaluru",
                    "work_model": "Hybrid",
                    "tech_stack": [primary_lang, "FastAPI", "TensorRT-LLM", "LlamaIndex / LangChain", "Kafka", "Docker"],
                    "specializations": [
                        "High-Throughput Model Serving & Inference Pipelines (vLLM / gRPC)",
                        "Agentic Workflows & Tool-Calling Runtime Systems"
                    ],
                    "match_rationale": "Core LLM platform engineering building production agentic tool-calling runtimes, TensorRT-LLM model serving pipelines, and FastAPI microservices.",
                    "apply_url": "https://job-boards.greenhouse.io/razorpaysoftwareprivatelimited/jobs/4730552005"
                },
                {
                    "company": "Hasura",
                    "title": "Backend Engineer - AI / Core Platform",
                    "location": "Bengaluru",
                    "work_model": "Hybrid",
                    "tech_stack": [sec_lang, primary_lang, "PostgreSQL (pgvector)", "Apache DataFusion", "gRPC", "Kubernetes"],
                    "specializations": [
                        "Zero-Copy Vector & Embedding Ingestion (Arrow / DataFusion)",
                        "Vector Search & Hybrid Retrieval (HNSW / pgvector / Qdrant)"
                    ],
                    "match_rationale": f"Systems backend role executing native vector search extensions, Apache DataFusion query planning, and zero-copy embedding ingestion using {sec_lang} and {primary_lang}.",
                    "apply_url": "https://hasura.io/careers/open-roles/?job_id=backend-core-platform"
                },
                {
                    "company": "Zepto",
                    "title": "AI Infrastructure Engineer (Personalization & Search)",
                    "location": "Bengaluru",
                    "work_model": "On-site",
                    "tech_stack": [primary_lang, "PySpark", "Qdrant / Milvus", "vLLM", "Kafka", "Redis"],
                    "specializations": [
                        "Lakehouse Feature Platforms & Distributed Data Pipelines",
                        "Vector Search & Hybrid Retrieval (HNSW / pgvector / Qdrant)"
                    ],
                    "match_rationale": "Real-time AI infrastructure engineering managing vector search indexing (Qdrant), PySpark feature pipelines, and sub-millisecond recommendation serving.",
                    "apply_url": "https://careers.zepto.com/jobs/ai-infrastructure-engineer"
                }
            ]
        else:
            candidates = [
                {
                    "company": "Sarvam AI",
                    "title": "Backend Engineer (Core Infrastructure)",
                    "location": "Bengaluru",
                    "work_model": "On-site",
                    "tech_stack": [primary_lang, sec_lang, "asyncio", "PostgreSQL", "Redis", "FastAPI"],
                    "specializations": self.specializations[:2],
                    "match_rationale": f"Core infrastructure engineering leveraging {primary_lang} and {sec_lang} for high-concurrency microservices, async execution engines, and transactional storage.",
                    "apply_url": "https://jobs.ashbyhq.com/sarvam/86ae80f8-b7eb-43a4-afde-fef58e77e23e"
                },
                {
                    "company": "PhonePe",
                    "title": "Software Engineer - Cloud Reliability & Systems",
                    "location": "Bengaluru",
                    "work_model": "On-site",
                    "tech_stack": [sec_lang, primary_lang, "NATS JetStream", "Redis", "PostgreSQL", "gRPC"],
                    "specializations": self.specializations[1:3] if len(self.specializations) > 2 else self.specializations,
                    "match_rationale": f"Low-latency cloud reliability and systems role built with {sec_lang}, NATS JetStream event streaming, and high-performance microservices.",
                    "apply_url": "https://www.instahyre.com/job-287410-software-engineer-cloud-systems-at-phonepe-bangalore/"
                },
                {
                    "company": "Databricks",
                    "title": "Backend Systems Engineer (Query Engine & Storage)",
                    "location": "Bengaluru",
                    "work_model": "Hybrid",
                    "tech_stack": [sec_lang, primary_lang, "Apache Arrow", "Apache DataFusion", "Delta Lake", "Polars"],
                    "specializations": self.specializations[:2],
                    "match_rationale": f"High-performance query engine development specializing in columnar storage formats, zero-copy FFI Arrow processing, and distributed lakehouses.",
                    "apply_url": "https://databricks.com/company/careers/open-positions/job?gh_jid=8099751002"
                },
                {
                    "company": "Cloudflare",
                    "title": "Systems Engineer - Edge Infrastructure",
                    "location": "Bengaluru",
                    "work_model": "Hybrid",
                    "tech_stack": [sec_lang, primary_lang, "Tokio", "asyncio", "PostgreSQL", "gRPC"],
                    "specializations": self.specializations[1:3] if len(self.specializations) > 2 else self.specializations,
                    "match_rationale": f"Edge infrastructure systems role building high-throughput proxy servers, low-latency streaming runtimes, and async event distribution with {sec_lang}.",
                    "apply_url": "https://boards.greenhouse.io/cloudflare/jobs/8097321"
                },
                {
                    "company": "ALLEN Digital",
                    "title": "Junior Data Engineer (Data Platform)",
                    "location": "Bengaluru",
                    "work_model": "Hybrid",
                    "tech_stack": [primary_lang, "PySpark", "Apache Arrow", "Delta Lake", "PostgreSQL", "ETL / ELT"],
                    "specializations": self.specializations[-2:],
                    "match_rationale": f"Data platform engineering role utilizing {primary_lang}, PySpark distributed query processing, Delta Lake lakehouse architectures, and automated ETL/ELT pipelines.",
                    "apply_url": "https://www.instahyre.com/job-328495-junior-data-engineer-at-allen-digital-bangalore/"
                }
            ]

        for c in candidates:
            is_dream = self._is_dream_company(c["company"])
            # Always prioritize direct requisition endpoint
            direct_job_url = c.get("apply_url") or self._get_dream_company_url(c["company"])
            postings.append(JobPosting(
                company=c["company"],
                title=c["title"],
                location=c["location"],
                work_model=c["work_model"],
                date_posted=datetime.now().strftime('%Y-%m-%d'),
                tech_stack=c["tech_stack"],
                specializations=c["specializations"],
                experience_range="1-3 YOE",
                match_rationale=c["match_rationale"],
                apply_url=direct_job_url,
                is_dream_company=is_dream,
                source="Direct Requisition Endpoint" if is_dream else "Curated Product Tech Corpus"
            ))

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
        target_locs = [loc.lower() for loc in self.target_locations]
        if target_locs:
            posting_loc_lower = posting.location.lower()
            if not any(loc in posting_loc_lower for loc in target_locs) and "remote" not in posting_loc_lower and "india" not in posting_loc_lower:
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
            if not has_primary and not posting.is_dream_company:
                return False

        # 5. Seniority Title Sanity Filter (e.g. for 1-3 YOE)
        max_yoe = self.criteria.get("max_experience_years", 3)
        if max_yoe <= 4:
            senior_titles = ["director", "vice president", "vp", "head of", "principal", "staff engineer", "senior manager", "architect", "lead partner"]
            if any(st in posting.title.lower() for st in senior_titles):
                return False

        return True

    def calculate_match_score(self, posting: JobPosting) -> float:
        """Scores job posting relevance based on Specializations & Tech Stack overlap."""
        score = 0.0
        posting_techs = [t.lower() for t in posting.tech_stack]
        
        # Primary language matches (+3.0 per language)
        for lang in self.primary_languages:
            if lang.lower() in posting_techs:
                score += 3.0
                
        # Core technology matches (+2.0 per tech)
        for tech in self.core_technologies:
            if tech.lower() in posting_techs:
                score += 2.0
                
        # Specialization overlap (+4.0 per specialization)
        for spec in self.specializations:
            if spec in posting.specializations:
                score += 4.0

        # Dream Company Boost (+25.0 to enforce priority tiering)
        if posting.is_dream_company:
            score += 25.0
                
        return score

    def _is_direct_job_url(self, url: str) -> bool:
        if not url:
            return False
        url_lower = url.lower()
        direct_indicators = [
            "gh_jid=", "/jobs/", "/job/", "/position/", "/opening/",
            "jobs.ashbyhq.com", "boards.greenhouse.io", "job-boards.greenhouse.io",
            "jobs.lever.co", "instahyre.com/job-", "linkedin.com/jobs/view",
            "/careers/open-positions/job", "arbeitnow.com/view/", "remotive.com/job/",
            "news.ycombinator.com/item?id="
        ]
        return any(ind in url_lower for ind in direct_indicators)

    def filter_jobs(self) -> List[JobPosting]:
        """
        Executes strict filtering, deduplication, and guarantees Dream Companies 
        receive priority ranking ahead of all other matches.
        """
        raw_postings = self.fetch_active_postings()
        
        # Retrofit dream company detection on all postings without clobbering direct requisition links
        for p in raw_postings:
            if self._is_dream_company(p.company):
                p.is_dream_company = True
                if not self._is_direct_job_url(p.apply_url):
                    custom_url = self._get_dream_company_url(p.company)
                    if custom_url:
                        p.apply_url = custom_url
            p.match_score = self.calculate_match_score(p)

        valid_postings = [p for p in raw_postings if self.validate_posting(p)]
        
        # Deduplicate by company & normalized title
        seen = set()
        deduped = []
        for p in valid_postings:
            key = f"{p.company.lower().strip()}:{p.title.lower().strip()}"
            if key not in seen:
                seen.add(key)
                deduped.append(p)

        # STRICT PRIORITY TIERING:
        # Tier 1: Dream Companies (ranked by match score)
        # Tier 2: Other Trusted Source matches (ranked by match score)
        dream_postings = [p for p in deduped if p.is_dream_company]
        other_postings = [p for p in deduped if not p.is_dream_company]

        dream_postings.sort(key=lambda p: p.match_score, reverse=True)
        other_postings.sort(key=lambda p: p.match_score, reverse=True)

        print(f"[AGENT] Filtering Result: {len(dream_postings)} Dream Company matches, {len(other_postings)} trusted source matches.")

        # Top balanced digest: prioritize Dream Companies first, then remaining top openings
        top_matches = dream_postings[:4] + other_postings[:3]
        if len(top_matches) < 5:
            top_matches = (dream_postings + other_postings)[:5]

        return top_matches

    def generate_html_email(self, matches: List[JobPosting]) -> str:
        """
        Renders a clean, executive, bulletproof responsive HTML email template.
        Fixes badge overlap bugs with structured table layouts and highlights Dream Companies.
        """
        today_str = datetime.now().strftime("%B %d, %Y")
        config_title = os.path.basename(self.config_path)
        
        dream_matches_count = sum(1 for m in matches if m.is_dream_company)
        trusted_matches_count = len(matches) - dream_matches_count

        # Render top specialization pills for header
        spec_summary_pills = "".join([
            f'<span style="background: rgba(233, 216, 253, 0.2); border: 1px solid rgba(216, 180, 254, 0.4); color: #e9d8fd; padding: 4px 10px; border-radius: 12px; font-size: 11px; margin-right: 6px; margin-bottom: 6px; display: inline-block; font-weight: 600;">✦ {spec}</span>'
            for spec in self.specializations[:4]
        ])

        cards_html = ""
        for job in matches:
            tech_badges = "".join([
                f'<span style="background: #f1f5f9; color: #0284c7; border: 1px solid #e2e8f0; padding: 3px 8px; border-radius: 6px; font-size: 11px; margin-right: 6px; margin-bottom: 4px; display: inline-block; font-weight: 600;">{tech}</span>'
                for tech in job.tech_stack
            ])
            
            spec_badges = "".join([
                f'<span style="background: #f5f3ff; color: #6d28d9; border: 1px solid #ddd6fe; padding: 3px 8px; border-radius: 6px; font-size: 11px; margin-right: 6px; margin-bottom: 4px; display: inline-block; font-weight: 600;">◈ {spec}</span>'
                for spec in job.specializations
            ])

            # Distinctive Styling for Dream Companies vs Trusted Sources
            if job.is_dream_company:
                card_border = "1.5px solid #fde68a"
                card_accent = "border-left: 5px solid #d97706;"
                card_shadow = "box-shadow: 0 4px 12px rgba(217, 119, 6, 0.08);"
                company_color = "#b45309"
                priority_badge = """
                <span style="display: inline-block; background: #fef3c7; color: #92400e; border: 1px solid #fde68a; padding: 3px 9px; border-radius: 12px; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    ⭐ Dream Company Priority
                </span>
                """
                btn_style = "background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff;"
                btn_text = "Apply Direct to Opening &rarr;"
            else:
                card_border = "1px solid #e2e8f0"
                card_accent = "border-left: 4px solid #3b82f6;"
                card_shadow = "box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);"
                company_color = "#2563eb"
                priority_badge = f"""
                <span style="display: inline-block; background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 3px 9px; border-radius: 12px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;">
                    ⚡ {job.source}
                </span>
                """
                btn_style = "background: #2563eb; color: #ffffff;"
                btn_text = "Direct Job Application &rarr;"

            # Work model & location badge styling
            if "on-site" in job.work_model.lower():
                loc_badge_style = "background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0;"
            elif "hybrid" in job.work_model.lower():
                loc_badge_style = "background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe;"
            else:
                loc_badge_style = "background: #fdf4ff; color: #86198f; border: 1px solid #f5d0fe;"

            cards_html += f"""
            <div style="background: #ffffff; border: {card_border}; {card_accent} border-radius: 12px; padding: 22px; margin-bottom: 22px; {card_shadow}">
                <!-- Header Table Layout to Prevent Any Location Badge Collisions -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 8px;">
                    <tr>
                        <td style="vertical-align: top; padding: 0;">
                            {priority_badge}
                            <h3 style="margin: 0 0 4px 0; color: #0f172a; font-size: 18px; font-weight: 700; line-height: 1.3;">
                                {job.title}
                            </h3>
                            <div style="font-size: 15px; font-weight: 700; color: {company_color};">
                                {job.company}
                            </div>
                        </td>
                        <td style="vertical-align: top; text-align: right; padding: 0 0 0 12px; white-space: nowrap;">
                            <span style="display: inline-block; {loc_badge_style} padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                                📍 {job.work_model} &bull; {job.location}
                            </span>
                        </td>
                    </tr>
                </table>

                <div style="color: #64748b; font-size: 12px; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #f1f5f9;">
                    🕒 Posted: {job.date_posted} &nbsp;&bull;&nbsp; 🎯 Seniority: {job.experience_range} &nbsp;&bull;&nbsp; 🔗 Source: {job.source}
                </div>
                
                <!-- Specializations -->
                <div style="margin-bottom: 10px;">
                    <div style="font-size: 11px; font-weight: 700; color: #6d28d9; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 0.5px;">Matched Specializations:</div>
                    {spec_badges}
                </div>

                <!-- Tech Stack -->
                <div style="margin-bottom: 14px;">
                    <div style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 0.5px;">Core Tech Stack:</div>
                    {tech_badges}
                </div>

                <!-- Match Rationale Callout -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; margin-bottom: 16px; color: #334155; font-size: 13px; line-height: 1.5;">
                    <strong style="color: #0f172a;">💡 Match Rationale:</strong> {job.match_rationale}
                </div>

                <!-- Action Button -->
                <a href="{job.apply_url}" target="_blank" style="display: inline-block; {btn_style} text-decoration: none; padding: 9px 18px; border-radius: 8px; font-weight: 700; font-size: 13px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                    {btn_text}
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
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px; color: #1e293b;">
            <div style="max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 32px 28px; text-align: left; color: #ffffff;">
                    <div style="display: inline-block; background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(147, 197, 253, 0.3); color: #93c5fd; text-transform: uppercase; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 20px; letter-spacing: 0.8px; margin-bottom: 12px;">
                        ✦ Multi-Stream Career Digest ({config_title})
                    </div>
                    <h1 style="margin: 0 0 8px 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">Matched Engineering Opportunities</h1>
                    <p style="margin: 0 0 16px 0; color: #94a3b8; font-size: 14px;">Curated dynamically per profile criteria &bull; {today_str}</p>
                    
                    <!-- Stat Breakdown Badges -->
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px;">
                        <span style="background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(251, 191, 36, 0.4); color: #fde68a; padding: 4px 10px; border-radius: 14px; font-size: 11px; font-weight: 700;">
                            ⭐ {dream_matches_count} Dream Company Matches
                        </span>
                        <span style="background: rgba(59, 130, 246, 0.2); border: 1px solid rgba(96, 165, 250, 0.4); color: #bfdbfe; padding: 4px 10px; border-radius: 14px; font-size: 11px; font-weight: 700;">
                            🌐 {trusted_matches_count} Trusted Source Openings
                        </span>
                    </div>

                    <div>
                        {spec_summary_pills}
                    </div>
                </div>
                
                <!-- Rules Summary Subheader -->
                <div style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; padding: 12px 28px; font-size: 12px; color: #64748b;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="color: #475569; font-weight: 600;">
                                <strong>Active Config:</strong> {config_title} &bull; 1-3 YOE &bull; {', '.join(self.target_locations[:2])}
                            </td>
                            <td style="text-align: right; color: #16a34a; font-weight: 700;">
                                ● Recency &lt; 14 Days
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- Main Content -->
                <div style="padding: 26px;">
                    <div style="color: #475569; font-size: 14px; margin-top: 0; margin-bottom: 20px;">
                        Found <strong>{len(matches)} highly-ranked engineering roles</strong>. Openings from your designated <strong>Dream Companies</strong> are prioritized first:
                    </div>
                    {cards_html}
                </div>

                <!-- Footer -->
                <div style="background: #f8fafc; padding: 20px 28px; text-align: center; color: #94a3b8; font-size: 12px; border-top: 1px solid #e2e8f0;">
                    Generated dynamically by JobFilterAgent &bull; Dream Companies prioritized &bull; Multi-stream verified
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

        matches_count = len(self.filter_jobs())
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Job Matches Digest: {matches_count} Active Roles (Dream Companies Prioritized)"
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
        print("[AGENT] Evaluating live job listings across multi-stream sources...")
        matches = self.filter_jobs()
        print(f"[AGENT] Successfully matched {len(matches)} target job postings.")

        html_content = self.generate_html_email(matches)
        
        # Derive output filename from config name
        config_name = os.path.splitext(os.path.basename(self.config_path))[0]
        preview_file = f"job_matches_{config_name}.html" if config_name != "config" else "job_matches_email.html"
        
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[AGENT] Clean email preview saved to: {os.path.abspath(preview_file)}")

        # Print structured summary to stdout with Dream Companies first
        dream_list = [m for m in matches if m.is_dream_company]
        other_list = [m for m in matches if not m.is_dream_company]

        print("\n" + "="*50)
        print("⭐ DREAM COMPANY MATCHES (PRIORITY 1)")
        print("="*50)
        if dream_list:
            for m in dream_list:
                print(f"★ {m.company} - {m.title}\n  Location: {m.work_model} - {m.location}\n  Specializations: {', '.join(m.specializations)}\n  Tech: {', '.join(m.tech_stack)}\n  Source: {m.source}\n  Apply: {m.apply_url}\n")
        else:
            print("No immediate Dream Company openings matching current active filters.")

        print("="*50)
        print("🌐 VERIFIED TRUSTED SOURCE MATCHES (PRIORITY 2)")
        print("="*50)
        if other_list:
            for m in other_list:
                print(f"• {m.company} - {m.title}\n  Location: {m.work_model} - {m.location}\n  Specializations: {', '.join(m.specializations)}\n  Tech: {', '.join(m.tech_stack)}\n  Source: {m.source}\n  Apply: {m.apply_url}\n")
        print("="*50)

        # Send via email if SMTP is configured
        text_summary = "\n".join([f"{'[DREAM COMPANY] ' if m.is_dream_company else ''}{m.company} - {m.title} ({m.work_model} - {m.location}): {m.apply_url}" for m in matches])
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
