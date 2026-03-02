from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from app.core.config import get_settings
from app.core.observability import LLM_CACHE_HITS, LLM_CACHE_MISSES
from app.core.redis_client import get_redis_client
from app.services.parser.section_parser import SectionParser

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    tokens: int | None = None
    model: str | None = None


class ContactNameModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None
    confidence: float


class ContactEmailModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    confidence: float


class ContactPhoneModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phone: str
    confidence: float


class ContactLocationModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str | None
    state: str | None
    country: str | None
    confidence: float


class ContactUrlsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    linkedin: str | None
    github: str | None
    websites: list[str]


class ContactModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: ContactNameModel
    emails: list[ContactEmailModel]
    phones: list[ContactPhoneModel]
    location: ContactLocationModel
    urls: ContactUrlsModel


class WorkExperienceItemModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: str | None
    client: str | None
    title: str | None
    start_date: str | None
    end_date: str | None
    is_current: bool
    location: str | None
    bullets: list[str]
    description: str | None


class EducationEntryModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: str | None = Field(
        default=None,
        validation_alias=AliasChoices("institution", "university", "college"),
    )
    degree: str | None = Field(
        default=None,
        validation_alias=AliasChoices("degree", "degree_name"),
    )
    field_of_study: str | None = Field(
        default=None,
        validation_alias=AliasChoices("field_of_study", "field", "major"),
    )
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None
    honors: str | None = None


class StructuredResumeModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contact: ContactModel
    work_experience: list[WorkExperienceItemModel]
    education: list[EducationEntryModel]
    skills: list[str]
    certifications: list[CertificationEntryModel]


class StructuredResumeContactEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contact: ContactModel


class StructuredResumeWorkEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    work_experience: list[WorkExperienceItemModel]


class StructuredResumeEducationEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    education: list[EducationEntryModel]


class StructuredResumeSkillsEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skills: list[str]


class StructuredResumeCertificationsEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    certifications: list[CertificationEntryModel]


class CertificationEntryModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None
    issuing_organization: str | None = Field(
        default=None,
        validation_alias=AliasChoices("issuing_organization", "issuer", "issuing_org"),
    )
    issue_date: str | None
    expiry_date: str | None
    credential_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("credential_id", "credential", "credentialid"),
    )
    is_active: bool | None
    confidence: float


class WorkExperienceDetailsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("company_name", "company"),
    )
    job_title: str | None = Field(
        default=None,
        validation_alias=AliasChoices("job_title", "title"),
    )
    start_date: str | None
    end_date: str | None
    is_current: bool
    location: str | None
    technologies: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("responsibilities", "bullets"),
    )


class LLMParsingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._cache: dict[str, tuple[float, LLMResponse]] = {}
        self._rate_timestamps: list[float] = []

        self._base_system_prompt = (
            "You are an Enterprise Resume Parsing AI built for high-accuracy "
            "recruitment systems.\n\n"
            "You specialize in:\n"
            "• US-format resumes\n"
            "• MS graduates\n"
            "• Senior professionals (2–20 pages)\n"
            "• Contract and federal resumes\n\n"
            "STRICT RULES:\n"
            "1. Never hallucinate information.\n"
            "2. Extract only from the provided resume text.\n"
            "3. If data is missing, return null.\n"
            "4. Normalize skills, degrees, certifications using taxonomy if available.\n"
            "5. Infer implicit technical skills only when clearly supported by responsibilities.\n"
            "6. Preserve chronological order (latest first).\n"
            "7. Do not merge different companies/roles.\n"
            "8. Return STRICT JSON only.\n"
            "9. No explanations, no extra text.\n"
            "10. Dates must be in YYYY-MM format when available.\n\n"
            "Output must follow the provided JSON schema exactly.\n\n"
        )

    def _structured_resume_default_payload(self) -> dict[str, Any]:
        return self._structured_resume_defaults()

    def _call_llm_validated(
        self,
        prompt: str,
        task: str,
        *,
        expect_array: bool,
        adapter: TypeAdapter,
        default_payload: Any,
        max_validation_retries: int = 2,
    ) -> Any:
        last_error: str | None = None
        for attempt in range(max_validation_retries + 1):
            attempt_task = task if attempt == 0 else f"{task}_validate_retry_{attempt}"
            attempt_prompt = prompt
            if attempt > 0 and last_error:
                attempt_prompt = (
                    f"{prompt}\n\n"
                    "The previous output was invalid and did not match the required schema. "
                    "Fix the output and return ONLY valid JSON.\n\n"
                    f"Validation errors:\n{last_error}\n"
                )
            response = self._call_llm(attempt_prompt, task=attempt_task)
            parsed = self._parse_json(response.content, expect_array=expect_array)
            try:
                return adapter.validate_python(parsed)
            except ValidationError as exc:
                last_error = json.dumps(exc.errors(), ensure_ascii=False)
                logger.warning(
                    "LLM schema validation failed",
                    extra={"task": task, "attempt": attempt + 1, "errors": exc.errors()},
                )

        try:
            return adapter.validate_python(default_payload)
        except ValidationError:
            return default_payload

    def extract_structured_resume(self, text: str) -> dict[str, Any]:
        sections = SectionParser().parse(text)
        experience_text = sections.get("experience").content if "experience" in sections else ""
        education_text = sections.get("education").content if "education" in sections else ""
        skills_text = sections.get("skills").content if "skills" in sections else ""
        certifications_text = (
            sections.get("certifications").content if "certifications" in sections else ""
        )
        contact_source = (
            sections.get("contact").content if "contact" in sections else text
        )

        default_payload = self._structured_resume_default_payload()
        contact_adapter = TypeAdapter(StructuredResumeContactEnvelope)
        work_adapter = TypeAdapter(StructuredResumeWorkEnvelope)
        education_adapter = TypeAdapter(StructuredResumeEducationEnvelope)
        skills_adapter = TypeAdapter(StructuredResumeSkillsEnvelope)
        certifications_adapter = TypeAdapter(StructuredResumeCertificationsEnvelope)
        resume_adapter = TypeAdapter(StructuredResumeModel)

        contact_env = self._call_llm_validated(
            self._structured_resume_contact_prompt(contact_source),
            "structured_resume_contact",
            expect_array=False,
            adapter=contact_adapter,
            default_payload={"contact": default_payload["contact"]},
        )

        work_env = self._call_llm_validated(
            self._structured_resume_work_prompt(experience_text or text),
            "structured_resume_work",
            expect_array=False,
            adapter=work_adapter,
            default_payload={"work_experience": default_payload["work_experience"]},
        )

        education_env = self._call_llm_validated(
            self._structured_resume_education_prompt(education_text or text),
            "structured_resume_education",
            expect_array=False,
            adapter=education_adapter,
            default_payload={"education": default_payload["education"]},
        )

        skills_env = self._call_llm_validated(
            self._structured_resume_skills_prompt(skills_text or text),
            "structured_resume_skills",
            expect_array=False,
            adapter=skills_adapter,
            default_payload={"skills": default_payload["skills"]},
        )

        certifications_env = self._call_llm_validated(
            self._structured_resume_certifications_prompt(certifications_text or text),
            "structured_resume_certifications",
            expect_array=False,
            adapter=certifications_adapter,
            default_payload={"certifications": default_payload["certifications"]},
        )

        def _dump_models(value: Any) -> Any:
            if isinstance(value, BaseModel):
                return value.model_dump()
            if isinstance(value, list):
                return [_dump_models(item) for item in value]
            if isinstance(value, dict):
                return {key: _dump_models(val) for key, val in value.items()}
            return value

        merged_payload = {
            "contact": _dump_models(
                getattr(contact_env, "contact", default_payload["contact"])
            ),
            "work_experience": _dump_models(
                getattr(work_env, "work_experience", default_payload["work_experience"])
            ),
            "education": _dump_models(
                getattr(education_env, "education", default_payload["education"])
            ),
            "skills": _dump_models(getattr(skills_env, "skills", default_payload["skills"])),
            "certifications": _dump_models(
                getattr(
                    certifications_env,
                    "certifications",
                    default_payload["certifications"],
                )
            ),
        }

        self._fill_structured_work_clients(
            merged_payload.get("work_experience"),
            experience_text or text,
        )

        validated = self._call_llm_validated(
            self._structured_resume_from_parts_prompt(
                merged_payload,
                certifications_text=certifications_text,
            ),
            "structured_resume_merge_validate",
            expect_array=False,
            adapter=resume_adapter,
            default_payload=default_payload,
            max_validation_retries=0,
        )
        if isinstance(validated, BaseModel):
            return validated.model_dump()
        return validated

    def normalize_structured_resume(self, payload: dict[str, Any]) -> dict[str, Any]:
        adapter = TypeAdapter(StructuredResumeModel)
        default_payload = self._structured_resume_default_payload()
        data = self._call_llm_validated(
            self._structured_resume_normalize_prompt(payload),
            "structured_resume_normalize",
            expect_array=False,
            adapter=adapter,
            default_payload=default_payload,
        )
        if isinstance(data, BaseModel):
            return data.model_dump()
        return data

    def verify_structured_resume(
        self, resume_text: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        adapter = TypeAdapter(StructuredResumeModel)
        default_payload = self._structured_resume_default_payload()
        data = self._call_llm_validated(
            self._structured_resume_verify_prompt(resume_text, payload),
            "structured_resume_verify",
            expect_array=False,
            adapter=adapter,
            default_payload=default_payload,
        )
        if isinstance(data, BaseModel):
            return data.model_dump()
        return data

    def extract_experience_skills(self, text: str) -> dict[str, Any]:
        chunks = self._chunk_text(text)
        if len(chunks) == 1:
            prompt = self._experience_skills_prompt(chunks[0])
            response = self._call_llm(prompt, task="experience_skills")
            data = self._parse_json(response.content, expect_array=False)
            return data or {"skills": []}

        all_skills: list[str] = []
        for idx, chunk in enumerate(chunks, start=1):
            prompt = self._experience_skills_prompt(
                chunk, header=f"Chunk {idx} of {len(chunks)}"
            )
            response = self._call_llm(prompt, task=f"experience_skills_{idx}")
            data = self._parse_json(response.content, expect_array=False)
            if isinstance(data, dict):
                skills = data.get("skills", [])
                if isinstance(skills, list):
                    all_skills.extend([s for s in skills if isinstance(s, str)])
        return {"skills": self._unique_list(all_skills)}

    def extract_all_skills_grouped(self, text: str) -> dict[str, Any]:
        chunks = self._chunk_text(text)
        if len(chunks) == 1:
            prompt = self._skills_grouped_prompt(chunks[0])
            response = self._call_llm(prompt, task="skills_grouped")
            data = self._parse_json(response.content, expect_array=False)
            return data or {
                "skills": {
                    "programming_languages": [],
                    "frameworks": [],
                    "databases": [],
                    "cloud_devops": [],
                    "tools": [],
                }
            }

        merged = {
            "skills": {
                "programming_languages": [],
                "frameworks": [],
                "databases": [],
                "cloud_devops": [],
                "tools": [],
            }
        }
        for idx, chunk in enumerate(chunks, start=1):
            prompt = self._skills_grouped_prompt(chunk, header=f"Chunk {idx} of {len(chunks)}")
            response = self._call_llm(prompt, task=f"skills_grouped_{idx}")
            data = self._parse_json(response.content, expect_array=False)
            if not isinstance(data, dict):
                continue
            skills = data.get("skills")
            if not isinstance(skills, dict):
                continue
            for key in merged["skills"].keys():
                values = skills.get(key, [])
                if isinstance(values, list):
                    merged["skills"][key] = self._unique_list(
                        merged["skills"][key] + [v for v in values if isinstance(v, str)]
                    )
        return merged

    def normalize_education_details(self, text: str) -> dict[str, Any]:
        chunks = self._chunk_text(text)
        if len(chunks) == 1:
            prompt = self._education_normalization_prompt(chunks[0])
            response = self._call_llm(prompt, task="education_normalization")
            data = self._parse_json(response.content, expect_array=False)
            return data or {}

        partials: list[dict[str, Any]] = []
        for idx, chunk in enumerate(chunks, start=1):
            prompt = self._education_normalization_prompt(
                chunk, header=f"Chunk {idx} of {len(chunks)}"
            )
            response = self._call_llm(prompt, task=f"education_normalization_{idx}")
            data = self._parse_json(response.content, expect_array=False)
            if isinstance(data, dict):
                partials.append(data)
        return self._merge_structured_resume(partials)

    def normalize_education_entries(self, text: str) -> list[dict[str, Any]]:
        chunks = self._chunk_text(text)
        adapter = TypeAdapter(list[EducationEntryModel])
        default_payload: list[dict[str, Any]] = []

        merged: list[dict[str, Any]] = []
        seen: set[str] = set()
        for idx, chunk in enumerate(chunks, start=1):
            prompt = self._education_entries_normalization_prompt(
                chunk, header=None if len(chunks) == 1 else f"Chunk {idx} of {len(chunks)}"
            )
            data = self._call_llm_validated(
                prompt,
                "education_entries_normalization" if len(chunks) == 1 else f"education_entries_normalization_{idx}",
                expect_array=True,
                adapter=adapter,
                default_payload=default_payload,
            )
            items: list[dict[str, Any]] = []
            if isinstance(data, list):
                items = [
                    item.model_dump() if isinstance(item, BaseModel) else item
                    for item in data
                    if isinstance(item, (BaseModel, dict))
                ]
            for item in items:
                key = "|".join(
                    [
                        str(item.get("institution") or "").strip().lower(),
                        str(item.get("degree") or "").strip().lower(),
                        str(item.get("field_of_study") or "").strip().lower(),
                        str(item.get("end_date") or "").strip().lower(),
                    ]
                )
                if not key.strip("|"):
                    continue
                if key in seen:
                    continue
                seen.add(key)
                merged.append(item)
        return merged

    def extract_work_experience_details(self, text: str) -> list[dict[str, Any]]:
        chunks = self._chunk_text(text)
        adapter = TypeAdapter(list[WorkExperienceDetailsModel])
        default_payload: list[dict[str, Any]] = []

        results: list[dict[str, Any]] = []
        for idx, chunk in enumerate(chunks, start=1):
            prompt = self._work_experience_prompt(
                chunk, header=None if len(chunks) == 1 else f"Chunk {idx} of {len(chunks)}"
            )
            data = self._call_llm_validated(
                prompt,
                "work_experience_details" if len(chunks) == 1 else f"work_experience_details_{idx}",
                expect_array=True,
                adapter=adapter,
                default_payload=default_payload,
            )
            if isinstance(data, list):
                results.extend(
                    [
                        item.model_dump() if isinstance(item, BaseModel) else item
                        for item in data
                        if isinstance(item, (BaseModel, dict))
                    ]
                )
        return results

    def extract_certifications(self, text: str) -> list[dict[str, Any]]:
        chunks = self._chunk_text(text)
        adapter = TypeAdapter(list[CertificationEntryModel])
        default_payload: list[dict[str, Any]] = []

        results: list[dict[str, Any]] = []
        for idx, chunk in enumerate(chunks, start=1):
            prompt = self._certifications_extraction_prompt(
                chunk, header=None if len(chunks) == 1 else f"Chunk {idx} of {len(chunks)}"
            )
            data = self._call_llm_validated(
                prompt,
                "certifications_extraction" if len(chunks) == 1 else f"certifications_extraction_{idx}",
                expect_array=True,
                adapter=adapter,
                default_payload=default_payload,
            )
            if isinstance(data, list):
                results.extend(
                    [
                        item.model_dump() if isinstance(item, BaseModel) else item
                        for item in data
                        if isinstance(item, (BaseModel, dict))
                    ]
                )
        return results

    def calculate_total_experience(self, structured_experience_json: str) -> dict[str, Any]:
        prompt = self._total_experience_prompt(structured_experience_json)
        response = self._call_llm(prompt, task="total_experience")
        data = self._parse_json(response.content, expect_array=False)
        return data or {}

    def evaluate_extraction_confidence(self, structured_payload: dict[str, Any]) -> dict[str, Any]:
        prompt = self._extraction_confidence_prompt(structured_payload)
        response = self._call_llm(prompt, task="extraction_confidence")
        data = self._parse_json(response.content, expect_array=False)
        return data or {}

    def normalize_deduplicate_skills(self, skills_array: list[Any]) -> dict[str, Any]:
        prompt = self._normalize_skills_prompt(skills_array)
        response = self._call_llm(prompt, task="normalize_skills")
        data = self._parse_json(response.content, expect_array=False)
        return data or {"normalized_skills": []}

    def verify_extracted_data(self, resume_text: str, extracted_payload: dict[str, Any]) -> dict[str, Any]:
        prompt = self._verification_prompt(resume_text, extracted_payload)
        response = self._call_llm(prompt, task="verify_extraction")
        data = self._parse_json(response.content, expect_array=False)
        return data or {}

    def _resume_intelligence_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + self._base_system_prompt + (
            "You are an enterprise Resume Parsing AI designed to extract structured "
            "data from professional resumes.\n\n"
            "You specialize in:\n"
            "• US-format resumes\n"
            "• MS graduates\n"
            "• Senior professionals (2–20 pages)\n"
            "• Contract and federal resumes\n\n"
            "Rules:\n"
            "1. Never hallucinate information.\n"
            "2. Extract only what exists in the resume.\n"
            "3. Normalize skills, degrees, and certifications.\n"
            "4. Infer implicit technical skills from experience.\n"
            "5. Return STRICT JSON only.\n"
            "6. If data is missing, return null.\n"
            "7. Do not add explanations.\n"
            "8. Maintain chronological order for experience.\n"
            "9. Support long resumes (10–20 pages).\n"
            "10. Ensure high accuracy.\n\n"
            "Follow the provided schema exactly and populate the following sections:\n\n"
            "1. Candidate Information\n"
            "   - Full Name\n"
            "   - Email\n"
            "   - Phone\n"
            "   - Location\n"
            "   - LinkedIn\n"
            "   - Visa / Work Authorization (if available)\n\n"
            "2. Professional Summary\n"
            "   - Years of Experience\n"
            "   - Primary Role (Full Stack / Data Engineer / Java / DevOps etc.)\n"
            "   - Seniority Level\n\n"
            "3. Technical Skills (Categorized)\n"
            "   Frontend:\n"
            "   Backend:\n"
            "   Programming Languages:\n"
            "   Frameworks:\n"
            "   Databases:\n"
            "   Cloud Platforms:\n"
            "   DevOps Tools:\n"
            "   Data Engineering Tools:\n"
            "   Testing Tools:\n"
            "   BI / Visualization:\n"
            "   Messaging / Streaming:\n"
            "   Operating Systems:\n"
            "   Other Tools:\n\n"
            "4. Project / Client Experience (chronological)\n"
            "   For each client extract:\n"
            "   - Client Name\n"
            "   - Role\n"
            "   - Duration\n"
            "   - Location\n"
            "   - Industry\n"
            "   - Responsibilities (summary)\n"
            "   - Technologies Used\n"
            "   - Environment\n\n"
            "5. Architecture & Enterprise Experience\n"
            "   - Microservices\n"
            "   - Distributed Systems\n"
            "   - Data Platforms\n"
            "   - ML Pipelines\n"
            "   - Event Streaming\n"
            "   - API Gateways\n"
            "   - Security Implementations\n\n"
            "6. Cloud & DevOps Experience\n"
            "   - CI/CD tools\n"
            "   - Containerization\n"
            "   - Infrastructure as Code\n"
            "   - Monitoring tools\n\n"
            "7. Education\n\n"
            "8. Certifications\n\n"
            "9. Domain Experience\n"
            "   - Banking\n"
            "   - Retail\n"
            "   - Healthcare\n"
            "   - Telecom\n"
            "   - Finance\n"
            "   - Ecommerce\n\n"
            "Normalize all skills (example: React.js = ReactJS = React).\n\n"
            "Return output strictly in JSON format for database storage.\n\n"
            f"Resume Text:\n{text}"
        )

    def _resume_type_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + (
            "Classify the resume type.\n\n"
            "Options:\n"
            "• Fresher Resume\n"
            "• Mid-Level Resume\n"
            "• Senior Resume\n"
            "• Academic CV\n"
            "• Federal Resume\n"
            "• Consultant Resume\n\n"
            "Resume Text:\n"
            f"\"\"\"\n{text}\n\"\"\"\n\n"
            "Return:\n\n"
            '{\n  "resume_type": ""\n}\n'
        )

    def _resume_sections_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + (
            "Identify all sections present in the resume.\n\n"
            "Possible sections:\n\n"
            "• Summary\n"
            "• Skills\n"
            "• Work Experience\n"
            "• Education\n"
            "• Certifications\n"
            "• Projects\n"
            "• Publications\n"
            "• Awards\n\n"
            "Resume Text:\n"
            f"\"\"\"\n{text}\n\"\"\"\n\n"
            "Return:\n\n"
            '{\n  "sections_detected": []\n}\n'
        )

    def _personal_info_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + self._base_system_prompt + (
            "You are a Senior Resume Parsing AI trained to analyze resumes of candidates "
            "with 10–20+ years of professional experience across US and global job markets.\n\n"
            "Your task is to extract and structure PERSONAL INFORMATION from the given resume text.\n\n"
            "Follow these extraction rules strictly:\n\n"
            "-----------------------------\n"
            "GENERAL RULES\n"
            "-----------------------------\n"
            "1. Extract only information explicitly present in the resume.\n"
            "2. Do NOT hallucinate or assume missing values.\n"
            "3. If data is not available, return empty string \"\" or empty array [].\n"
            "4. Ignore recruiter details, company contacts, and references.\n"
            "5. Normalize all URLs to full format (https://…).\n"
            "6. Handle multi-page senior resumes intelligently.\n\n"
            "-----------------------------\n"
            "NAME HANDLING\n"
            "-----------------------------\n"
            "1. Extract full legal name.\n"
            "2. Split into:\n"
            "   - first_name\n"
            "   - middle_name\n"
            "   - last_name\n"
            "3. Ignore certifications next to names (e.g., PMP, PhD).\n\n"
            "-----------------------------\n"
            "CONTACT DETAILS\n"
            "-----------------------------\n"
            "1. Extract ALL emails → return as array.\n"
            "2. Extract ALL phone numbers → return as array.\n"
            "3. Normalize international formats (+1, +91, etc.).\n\n"
            "-----------------------------\n"
            "LOCATION HANDLING\n"
            "-----------------------------\n"
            "1. Extract current location only.\n"
            "2. Structure into:\n"
            "   - city\n"
            "   - state\n"
            "   - country\n"
            "   - zip_code\n"
            "3. Capture relocation openness if mentioned.\n\n"
            "-----------------------------\n"
            "SOCIAL LINKS\n"
            "-----------------------------\n"
            "Extract and normalize:\n\n"
            "• LinkedIn\n"
            "• GitHub\n"
            "• Portfolio\n"
            "• Personal Website\n\n"
            "Also extract usernames from URLs.\n\n"
            "-----------------------------\n"
            "VISA & WORK AUTHORIZATION (VERY IMPORTANT)\n"
            "-----------------------------\n"
            "Detect and classify:\n\n"
            "Visa Types:\n"
            "- US Citizen\n"
            "- Green Card / Permanent Resident\n"
            "- H1B\n"
            "- H4 EAD\n"
            "- L2 EAD\n"
            "- OPT\n"
            "- STEM OPT\n"
            "- CPT\n"
            "- TN Visa\n\n"
            "Work Authorization Phrases:\n"
            "- \"Authorized to work in the US\"\n"
            "- \"Requires sponsorship\"\n"
            "- \"No sponsorship required\"\n"
            "- \"H1B transfer required\"\n\n"
            "Infer sponsorship requirement.\n\n"
            "-----------------------------\n"
            "ADDITIONAL SENIOR FIELDS\n"
            "-----------------------------\n"
            "Extract if available:\n\n"
            "• Nationality\n"
            "• Date of Birth\n"
            "• Languages\n"
            "• Security Clearance\n"
            "• Veteran Status\n"
            "• Open to Remote\n"
            "• Open to Relocation\n\n"
            "-----------------------------\n"
            "OUTPUT FORMAT\n"
            "-----------------------------\n"
            "Return ONLY valid JSON in the structure below.\n"
            "No explanation text.\n\n"
            "Resume Text:\n"
            f"\"\"\"\n{text}\n\"\"\"\n\n"
            "{\n"
            '  "personal_info": {\n'
            '    "full_name": "",\n'
            '    "first_name": "",\n'
            '    "middle_name": "",\n'
            '    "last_name": "",\n\n'
            '    "emails": [],\n'
            '    "phones": [],\n\n'
            '    "current_location": {\n'
            '      "city": "",\n'
            '      "state": "",\n'
            '      "country": "",\n'
            '      "zip_code": ""\n'
            "    },\n\n"
            '    "linkedin": "",\n'
            '    "linkedin_username": "",\n\n'
            '    "github": "",\n'
            '    "github_username": "",\n\n'
            '    "portfolio": "",\n'
            '    "website": "",\n\n'
            '    "visa_status": "",\n'
            '    "work_authorization": "",\n'
            '    "requires_sponsorship": "",\n\n'
            '    "open_to_relocation": "",\n'
            '    "open_to_remote": "",\n\n'
            '    "nationality": "",\n'
            '    "date_of_birth": "",\n\n'
            '    "languages": [],\n'
            '    "security_clearance": "",\n'
            '    "veteran_status": ""\n'
            "  }\n"
            "}\n"
        )

    def _education_entries_normalization_prompt(
        self, text: str, header: str | None = None
    ) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + self._base_system_prompt + (
            "You are an Education Normalization AI.\n\n"
            "Return ONLY valid JSON. No markdown. No explanations.\n\n"
            "Task:\n"
            "- Extract ALL education items from the provided text (degrees, diplomas, intermediate/secondary, certificates if they represent formal schooling).\n"
            "- Normalize fields but NEVER guess. If unknown, use null.\n"
            "- Dates: If you see a range like '2022-2024', use start_date='2022' and end_date='2024'.\n"
            "- For board-style education, use the board name as institution when present.\n\n"
            "Input Text:\n"
            f"\"\"\"\n{text}\n\"\"\"\n\n"
            "Return JSON array with objects exactly shaped like:\n\n"
            "[\n"
            "  {\n"
            '    "institution": null,\n'
            '    "degree": null,\n'
            '    "field_of_study": null,\n'
            '    "start_date": null,\n'
            '    "end_date": null,\n'
            '    "gpa": null,\n'
            '    "honors": null,\n'
            '    "in_progress": false,\n'
            '    "confidence": 0.0\n'
            "  }\n"
            "]\n"
        )

    def _structured_resume_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + self._base_system_prompt + (
            "You are a resume parsing engine.\n\n"
            "Return ONLY valid JSON. No markdown. No explanations. No extra keys.\n"
            "If a value is not present, use null. Never guess.\n\n"
            "JSON schema (return exactly this shape):\n\n"
            "{\n"
            '  "contact": {\n'
            '    "name": {"name": null, "confidence": 0.0},\n'
            '    "emails": [{"email": "", "confidence": 0.0}],\n'
            '    "phones": [{"phone": "", "confidence": 0.0}],\n'
            '    "location": {"city": null, "state": null, "country": null, "confidence": 0.0},\n'
            '    "urls": {"linkedin": null, "github": null, "websites": []}\n'
            "  },\n"
            '  "work_experience": [\n'
            "    {\n"
            '      "company": null,\n'
            '      "client": null,\n'
            '      "title": null,\n'
            '      "start_date": null,\n'
            '      "end_date": null,\n'
            '      "is_current": false,\n'
            '      "location": null,\n'
            '      "bullets": [],\n'
            '      "description": null\n'
            "    }\n"
            "  ],\n"
            '  "education": [],\n'
            '  "skills": []\n'
            "}\n\n"
            "Rules:\n"
            "- Extract client names if text indicates \"Client:\", \"End Client:\", \"Project for <client>\", or similar.\n"
            "- Do not invent companies/clients.\n"
            "- Dates: keep raw as seen (do not normalize in this pass).\n"
            "- Output must be a single JSON object.\n\n"
            "Few-shot examples (follow these patterns exactly):\n\n"
            "Example 1 (multiple emails):\n"
            "Resume Text:\n"
            '"""\n'
            "ALEX CARTER\n"
            "alex.carter@company.com | alex.carter@gmail.com\n"
            "+1 (415) 555-1001\n"
            "San Francisco, CA\n"
            "LinkedIn: https://linkedin.com/in/alexcarter\n"
            "Skills: Python, AWS, Docker\n"
            '"""\n'
            "Output JSON:\n"
            "{\n"
            "  \"contact\": {\n"
            "    \"name\": {\"name\": \"Alex Carter\", \"confidence\": 0.9},\n"
            "    \"emails\": [\n"
            "      {\"email\": \"alex.carter@company.com\", \"confidence\": 0.9},\n"
            "      {\"email\": \"alex.carter@gmail.com\", \"confidence\": 0.9}\n"
            "    ],\n"
            "    \"phones\": [{\"phone\": \"+1 (415) 555-1001\", \"confidence\": 0.9}],\n"
            "    \"location\": {\"city\": \"San Francisco\", \"state\": \"CA\", \"country\": null, \"confidence\": 0.8},\n"
            "    \"urls\": {\"linkedin\": \"https://linkedin.com/in/alexcarter\", \"github\": null, \"websites\": []}\n"
            "  },\n"
            "  \"work_experience\": [\n"
            "    {\n"
            "      \"company\": null,\n"
            "      \"client\": null,\n"
            "      \"title\": null,\n"
            "      \"start_date\": null,\n"
            "      \"end_date\": null,\n"
            "      \"is_current\": false,\n"
            "      \"location\": null,\n"
            "      \"bullets\": [],\n"
            "      \"description\": null\n"
            "    }\n"
            "  ],\n"
            "  \"education\": [],\n"
            "  \"skills\": [\"python\", \"aws\", \"docker\"]\n"
            "}\n\n"

            "Example 2 (contract role with client + messy date range):\n"
            "Resume Text:\n"
            '"""\n'
            "PRIYA SHARMA\n"
            "priya.sharma@example.com\n"
            "+1 212 555 2002\n"
            "New York, NY\n"
            "\n"
            "CONTRACT EXPERIENCE\n"
            "ABC Consulting (Vendor) - Sr. Java Developer\n"
            "Client: BigBank Corp\n"
            "Jan 2021 – Present\n"
            "- Built microservices in Spring Boot\n"
            "- Deployed to AWS\n"
            '"""\n'
            "Output JSON:\n"
            "{\n"
            "  \"contact\": {\n"
            "    \"name\": {\"name\": \"Priya Sharma\", \"confidence\": 0.9},\n"
            "    \"emails\": [{\"email\": \"priya.sharma@example.com\", \"confidence\": 0.9}],\n"
            "    \"phones\": [{\"phone\": \"+1 212 555 2002\", \"confidence\": 0.8}],\n"
            "    \"location\": {\"city\": \"New York\", \"state\": \"NY\", \"country\": null, \"confidence\": 0.8},\n"
            "    \"urls\": {\"linkedin\": null, \"github\": null, \"websites\": []}\n"
            "  },\n"
            "  \"work_experience\": [\n"
            "    {\n"
            "      \"company\": \"ABC Consulting\",\n"
            "      \"client\": \"BigBank Corp\",\n"
            "      \"title\": \"Sr. Java Developer\",\n"
            "      \"start_date\": \"Jan 2021\",\n"
            "      \"end_date\": \"Present\",\n"
            "      \"is_current\": true,\n"
            "      \"location\": \"New York, NY\",\n"
            "      \"bullets\": [\n"
            "        \"Built microservices in Spring Boot\",\n"
            "        \"Deployed to AWS\"\n"
            "      ],\n"
            "      \"description\": null\n"
            "    }\n"
            "  ],\n"
            "  \"education\": [],\n"
            "  \"skills\": [\"java\", \"spring boot\", \"aws\", \"microservices\"]\n"
            "}\n\n"

            "Example 3 (2-column style / scrambled lines):\n"
            "Resume Text:\n"
            '"""\n'
            "MICHAEL LEE            EXPERIENCE\n"
            "michael.lee@work.com    ACME INC — DATA ENGINEER\n"
            "mike.lee@yahoo.com      Feb 2019 - Mar 2022\n"
            "+1 (646) 555-3003       - Built ETL pipelines\n"
            "Austin TX              - Spark, Python, Airflow\n"
            "LinkedIn /in/michaellee\n"
            '"""\n'
            "Output JSON:\n"
            "{\n"
            "  \"contact\": {\n"
            "    \"name\": {\"name\": \"Michael Lee\", \"confidence\": 0.8},\n"
            "    \"emails\": [\n"
            "      {\"email\": \"michael.lee@work.com\", \"confidence\": 0.8},\n"
            "      {\"email\": \"mike.lee@yahoo.com\", \"confidence\": 0.8}\n"
            "    ],\n"
            "    \"phones\": [{\"phone\": \"+1 (646) 555-3003\", \"confidence\": 0.8}],\n"
            "    \"location\": {\"city\": \"Austin\", \"state\": \"TX\", \"country\": null, \"confidence\": 0.7},\n"
            "    \"urls\": {\"linkedin\": \"https://linkedin.com/in/michaellee\", \"github\": null, \"websites\": []}\n"
            "  },\n"
            "  \"work_experience\": [\n"
            "    {\n"
            "      \"company\": \"Acme Inc\",\n"
            "      \"client\": null,\n"
            "      \"title\": \"Data Engineer\",\n"
            "      \"start_date\": \"Feb 2019\",\n"
            "      \"end_date\": \"Mar 2022\",\n"
            "      \"is_current\": false,\n"
            "      \"location\": \"Austin TX\",\n"
            "      \"bullets\": [\n"
            "        \"Built ETL pipelines\",\n"
            "        \"Spark, Python, Airflow\"\n"
            "      ],\n"
            "      \"description\": null\n"
            "    }\n"
            "  ],\n"
            "  \"education\": [],\n"
            "  \"skills\": [\"python\", \"spark\", \"airflow\", \"etl\"]\n"
            "}\n\n"

            "Example 4 (messy date formats / ranges):\n"
            "Resume Text:\n"
            '"""\n'
            "SARA NG\n"
            "sara.ng@example.com\n"
            "+44 20 7946 0958\n"
            "London, UK\n"
            "\n"
            "Omega Systems - DevOps Engineer\n"
            "(03/2020 to 11/22)\n"
            "- CI/CD with GitHub Actions\n"
            "- Kubernetes, Terraform\n"
            '"""\n'
            "Output JSON:\n"
            "{\n"
            "  \"contact\": {\n"
            "    \"name\": {\"name\": \"Sara Ng\", \"confidence\": 0.8},\n"
            "    \"emails\": [{\"email\": \"sara.ng@example.com\", \"confidence\": 0.9}],\n"
            "    \"phones\": [{\"phone\": \"+44 20 7946 0958\", \"confidence\": 0.8}],\n"
            "    \"location\": {\"city\": \"London\", \"state\": null, \"country\": \"UK\", \"confidence\": 0.8},\n"
            "    \"urls\": {\"linkedin\": null, \"github\": null, \"websites\": []}\n"
            "  },\n"
            "  \"work_experience\": [\n"
            "    {\n"
            "      \"company\": \"Omega Systems\",\n"
            "      \"client\": null,\n"
            "      \"title\": \"DevOps Engineer\",\n"
            "      \"start_date\": \"03/2020\",\n"
            "      \"end_date\": \"11/22\",\n"
            "      \"is_current\": false,\n"
            "      \"location\": \"London, UK\",\n"
            "      \"bullets\": [\n"
            "        \"CI/CD with GitHub Actions\",\n"
            "        \"Kubernetes, Terraform\"\n"
            "      ],\n"
            "      \"description\": null\n"
            "    }\n"
            "  ],\n"
            "  \"education\": [],\n"
            "  \"skills\": [\"github actions\", \"kubernetes\", \"terraform\", \"ci/cd\"]\n"
            "}\n\n"

            "Resume text:\n"
            f"<<<TEXT>>>\n{text}\n<<<TEXT>>>\n"
        )

    def _structured_resume_contact_prompt(self, text: str) -> str:
        schema = {"contact": self._structured_resume_defaults()["contact"]}
        return self._base_system_prompt + (
            "Extract ONLY the contact section from the provided text and return ONLY JSON.\n\n"
            "Schema (return exactly this shape; no extra keys):\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n\n"
            "Text:\n<<<TEXT>>>\n"
            f"{text}\n"
            "<<<TEXT>>>\n"
        )

    def _structured_resume_certifications_prompt(self, text: str) -> str:
        schema = {
            "certifications": [
                {
                    "name": None,
                    "issuing_organization": None,
                    "issue_date": None,
                    "expiry_date": None,
                    "credential_id": None,
                    "is_active": None,
                    "confidence": 0.0,
                }
            ]
        }
        return self._base_system_prompt + (
            "Extract ONLY certifications from the provided text and return ONLY JSON.\n\n"
            "Rules:\n"
            "- Include certifications, licenses, and credentials.\n"
            "- Do not include courses, workshops, or training sessions unless explicitly a certification/license.\n"
            "- Do not invent missing dates/ids/providers.\n\n"
            "Schema (return exactly this shape; no extra keys):\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n\n"
            "Text:\n<<<TEXT>>>\n"
            f"{text}\n"
            "<<<TEXT>>>\n"
        )

    def _structured_resume_work_prompt(self, text: str) -> str:
        schema = {"work_experience": self._structured_resume_defaults()["work_experience"]}
        return self._base_system_prompt + (
            "Extract ONLY work experience from the provided text and return ONLY JSON.\n\n"
            "Rules:\n"
            "- Keep each company/role separate.\n"
            "- Extract client names ONLY if explicitly indicated (examples: 'Client:', 'End Client:', 'Client -', 'Project for <client>', 'Worked for <client>').\n"
            "- Do not invent companies/clients.\n\n"
            "Schema (return exactly this shape; no extra keys):\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n\n"
            "Text:\n<<<TEXT>>>\n"
            f"{text}\n"
            "<<<TEXT>>>\n"
        )

    _STRUCTURED_CLIENT_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"\b(?:end\s+client|client)\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
        re.compile(r"\bproject\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
        re.compile(
            r"\bworked\s+for\s+(?P<client>[A-Za-z0-9][A-Za-z0-9 &.,()/-]{2,})",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bproject\s+for\s+(?P<client>[A-Za-z0-9][A-Za-z0-9 &.,()/-]{2,})",
            re.IGNORECASE,
        ),
    ]

    def _fill_structured_work_clients(self, items: Any, source_text: str) -> None:
        if not isinstance(items, list) or not source_text:
            return
        lines = [line.strip() for line in source_text.splitlines()]
        lowered_lines = [line.lower() for line in lines]

        def extract_from_block(block: str) -> str | None:
            if not block:
                return None
            for pattern in self._STRUCTURED_CLIENT_PATTERNS:
                match = pattern.search(block)
                if not match:
                    continue
                raw = (match.group("client") or "").strip().strip("-–—| ")
                raw = re.split(r"\s{2,}|\||\u2022", raw)[0].strip()
                raw = re.sub(r"\b\d{4}\b", "", raw).strip(" -–—|,;:")
                if not raw:
                    continue
                if len(raw) > 80:
                    continue
                return raw
            return None

        for item in items:
            if not isinstance(item, dict):
                continue
            existing_client = str(item.get("client") or "").strip()
            if existing_client:
                continue

            company = str(item.get("company") or "").strip()
            title = str(item.get("title") or "").strip()

            anchors = [a for a in (company, title) if a]
            if not anchors:
                continue

            anchor_idx: int | None = None
            for idx, line in enumerate(lowered_lines):
                if company and company.lower() in line:
                    anchor_idx = idx
                    if title and title.lower() not in line:
                        for forward in range(1, 4):
                            if idx + forward < len(lowered_lines) and title.lower() in lowered_lines[idx + forward]:
                                anchor_idx = idx
                                break
                    break
                if not company and title and title.lower() in line:
                    anchor_idx = idx
                    break

            if anchor_idx is None:
                continue

            start = anchor_idx
            end = min(len(lines), anchor_idx + 28)
            block = "\n".join(lines[start:end])
            client = extract_from_block(block)
            if not client:
                continue
            if company and client.lower() == company.lower():
                continue
            item["client"] = client

    def _structured_resume_education_prompt(self, text: str) -> str:
        schema = {
            "education": [
                {
                    "institution": None,
                    "degree": None,
                    "field_of_study": None,
                    "start_date": None,
                    "end_date": None,
                    "gpa": None,
                    "honors": None,
                }
            ]
        }
        return self._base_system_prompt + (
            "Extract ONLY education entries from the provided text and return ONLY JSON.\n\n"
            "Rules:\n"
            "- Do not infer education that is not present.\n\n"
            "Schema (return exactly this shape; no extra keys):\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n\n"
            "Text:\n<<<TEXT>>>\n"
            f"{text}\n"
            "<<<TEXT>>>\n"
        )

    def _structured_resume_skills_prompt(self, text: str) -> str:
        schema = {"skills": []}
        return self._base_system_prompt + (
            "Extract ONLY technical skills from the provided text and return ONLY JSON.\n\n"
            "Rules:\n"
            "- Return an array of strings.\n"
            "- No explanations; no extra keys.\n\n"
            "Schema (return exactly this shape; no extra keys):\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n\n"
            "Text:\n<<<TEXT>>>\n"
            f"{text}\n"
            "<<<TEXT>>>\n"
        )

    def extract_technical_skills_only(self, resume_text: str) -> list[str]:
        """STEP 4 — LLM fallback: extract only technical skills from resume text.
        Used to validate skills not in DB; if LLM returns a skill, mark as source='llm'."""
        if not (resume_text and resume_text.strip()):
            return []
        prompt = (
            self._base_system_prompt
            + "Extract only technical skills from this resume text.\n"
            "Return only a clean comma-separated list.\n"
            "Do not include soft skills.\n\n"
            f"Resume text:\n<<<TEXT>>>\n{resume_text[:8000]}\n<<<TEXT>>>\n"
        )
        response = self._call_llm(prompt, task="extract_technical_skills_only")
        content = (response.content or "").strip()
        if not content:
            return []
        # Parse comma-separated or JSON array
        content = content.strip("[]\"'")
        skills: list[str] = []
        for part in content.split(","):
            s = part.strip().strip("'\"").strip()
            if s and len(s) < 100:
                skills.append(s)
        return skills

    def _structured_resume_from_parts_prompt(
        self,
        payload: dict[str, Any],
        *,
        certifications_text: str = "",
    ) -> str:
        schema = self._structured_resume_defaults()
        extra_context = (
            f"\n\nCertifications section (use only to fill certifications; do not mix into skills):\n<<<CERTS>>>\n{certifications_text}\n<<<CERTS>>>\n"
            if certifications_text.strip()
            else ""
        )
        return self._base_system_prompt + (
            "Validate and finalize the structured resume JSON. Return ONLY JSON.\n\n"
            "Rules:\n"
            "- Remove keys not in schema.\n"
            "- Do not invent missing items.\n"
            "- Ensure types match schema exactly.\n\n"
            "Schema:\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n\n"
            "Input JSON:\n<<<JSON>>>\n"
            f"{json.dumps(payload, ensure_ascii=False)}\n"
            "<<<JSON>>>\n"
            f"{extra_context}"
        )

    def _structured_resume_normalize_prompt(self, payload: dict[str, Any]) -> str:
        schema = self._structured_resume_defaults()
        return self._base_system_prompt + (
            "Normalize the following JSON and return ONLY JSON.\n\n"
            "Rules:\n"
            "- phones: convert to E.164 when possible, otherwise keep original\n"
            "- emails: lowercase\n"
            "- dates: normalize to ISO (YYYY-MM or YYYY-MM-DD when day is present)\n"
            "- normalized_name: lowercase, trimmed, single spaces\n"
            "- deduplicate obvious duplicates in emails/phones/skills\n"
            "- remove keys not in schema\n\n"
            "Schema (remove keys not present here; preserve shape and types):\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n\n"
            "JSON:\n"
            "<<<JSON>>>\n"
            f"{json.dumps(payload, ensure_ascii=False)}\n"
            "<<<JSON>>>\n"
        )

    def _structured_resume_verify_prompt(self, resume_text: str, payload: dict[str, Any]) -> str:
        schema = self._structured_resume_defaults()
        return self._base_system_prompt + (
            "Verify extracted data against resume text and return ONLY JSON.\n\n"
            "Rules:\n"
            "- Keep a field only if it is supported by the resume text.\n"
            "- If unsupported, set it to null (or remove the list entry if the entire entry is unsupported).\n"
            "- Do not invent missing items.\n"
            "- Remove any keys not in schema.\n\n"
            "Schema (remove keys not present here; preserve shape and types):\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n\n"
            "Resume text:\n"
            f"<<<TEXT>>>\n{resume_text}\n<<<TEXT>>>\n\n"
            "Candidate JSON:\n"
            "<<<JSON>>>\n"
            f"{json.dumps(payload, ensure_ascii=False)}\n"
            "<<<JSON>>>\n"
        )

    @staticmethod
    def _structured_resume_defaults() -> dict[str, Any]:
        return {
            "contact": {
                "name": {"name": None, "confidence": 0.0},
                "emails": [{"email": "", "confidence": 0.0}],
                "phones": [{"phone": "", "confidence": 0.0}],
                "location": {
                    "city": None,
                    "state": None,
                    "country": None,
                    "confidence": 0.0,
                },
                "urls": {"linkedin": None, "github": None, "websites": []},
            },
            "work_experience": [
                {
                    "company": None,
                    "client": None,
                    "title": None,
                    "start_date": None,
                    "end_date": None,
                    "is_current": False,
                    "location": None,
                    "bullets": [],
                    "description": None,
                }
            ],
            "education": [],
            "skills": [],
            "certifications": [],
        }

    @staticmethod
    def _coerce_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _coerce_bool(value: Any, default: bool = False) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "y", "1"}:
                return True
            if lowered in {"false", "no", "n", "0"}:
                return False
        if isinstance(value, (int, float)):
            return bool(value)
        return default

    @staticmethod
    def _coerce_str_or_none(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return str(value).strip() or None

    def _enforce_structured_resume_schema(self, payload: dict[str, Any]) -> dict[str, Any]:
        defaults = self._structured_resume_defaults()

        contact_in = payload.get("contact") if isinstance(payload.get("contact"), dict) else {}
        name_in = contact_in.get("name") if isinstance(contact_in.get("name"), dict) else {}
        emails_in = contact_in.get("emails") if isinstance(contact_in.get("emails"), list) else []
        phones_in = contact_in.get("phones") if isinstance(contact_in.get("phones"), list) else []
        location_in = (
            contact_in.get("location") if isinstance(contact_in.get("location"), dict) else {}
        )
        urls_in = contact_in.get("urls") if isinstance(contact_in.get("urls"), dict) else {}
        websites_in = urls_in.get("websites") if isinstance(urls_in.get("websites"), list) else []

        contact_out = {
            "name": {
                "name": self._coerce_str_or_none(name_in.get("name")),
                "confidence": self._coerce_float(name_in.get("confidence"), 0.0),
            },
            "emails": [
                {
                    "email": str(item.get("email", "")) if isinstance(item, dict) else "",
                    "confidence": self._coerce_float(
                        item.get("confidence"), 0.0
                    )
                    if isinstance(item, dict)
                    else 0.0,
                }
                for item in emails_in
                if isinstance(item, dict)
            ]
            or defaults["contact"]["emails"],
            "phones": [
                {
                    "phone": str(item.get("phone", "")) if isinstance(item, dict) else "",
                    "confidence": self._coerce_float(
                        item.get("confidence"), 0.0
                    )
                    if isinstance(item, dict)
                    else 0.0,
                }
                for item in phones_in
                if isinstance(item, dict)
            ]
            or defaults["contact"]["phones"],
            "location": {
                "city": self._coerce_str_or_none(location_in.get("city")),
                "state": self._coerce_str_or_none(location_in.get("state")),
                "country": self._coerce_str_or_none(location_in.get("country")),
                "confidence": self._coerce_float(location_in.get("confidence"), 0.0),
            },
            "urls": {
                "linkedin": self._coerce_str_or_none(urls_in.get("linkedin")),
                "github": self._coerce_str_or_none(urls_in.get("github")),
                "websites": [str(item).strip() for item in websites_in if str(item).strip()],
            },
        }

        work_in = payload.get("work_experience") if isinstance(payload.get("work_experience"), list) else []
        work_out = []
        for item in work_in:
            if not isinstance(item, dict):
                continue
            work_out.append(
                {
                    "company": self._coerce_str_or_none(item.get("company")),
                    "client": self._coerce_str_or_none(item.get("client")),
                    "title": self._coerce_str_or_none(item.get("title")),
                    "start_date": self._coerce_str_or_none(item.get("start_date")),
                    "end_date": self._coerce_str_or_none(item.get("end_date")),
                    "is_current": self._coerce_bool(item.get("is_current"), False),
                    "location": self._coerce_str_or_none(item.get("location")),
                    "bullets": [
                        str(b).strip()
                        for b in (item.get("bullets") if isinstance(item.get("bullets"), list) else [])
                        if str(b).strip()
                    ],
                    "description": self._coerce_str_or_none(item.get("description")),
                }
            )
        if not work_out:
            work_out = defaults["work_experience"]

        education_out = payload.get("education") if isinstance(payload.get("education"), list) else []
        skills_out = payload.get("skills") if isinstance(payload.get("skills"), list) else []
        certifications_out = (
            payload.get("certifications")
            if isinstance(payload.get("certifications"), list)
            else []
        )

        return {
            "contact": contact_out,
            "work_experience": work_out,
            "education": education_out,
            "skills": skills_out,
            "certifications": certifications_out,
        }

    def _experience_skills_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + (
            "From the following work experience text, extract ALL technical skills.\n\n"
            "Instructions:\n\n"
            "1. Include explicitly mentioned skills.\n"
            "2. Infer implicit skills from tools, frameworks, and platforms.\n"
            "3. Normalize to standard industry names.\n"
            "4. Remove duplicates.\n"
            "5. Ignore soft skills unless technical.\n\n"
            "Text:\n"
            f"\"\"\"\n{text}\n\"\"\"\n\n"
            "Return:\n\n"
            '{\n  "skills": []\n}\n'
        )

    def _skills_grouped_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + self._base_system_prompt + (
            "Extract all skills.\n\n"
            "Instructions:\n\n"
            "1. Include technical skills only.\n"
            "2. Group into:\n"
            "   • Programming Languages\n"
            "   • Frameworks\n"
            "   • Databases\n"
            "   • Cloud/DevOps\n"
            "   • Tools\n"
            "3. Normalize names.\n"
            "4. Remove duplicates.\n\n"
            "Resume Text:\n"
            f"\"\"\"\n{text}\n\"\"\"\n\n"
            "Return:\n\n"
            "{\n"
            '  "skills": {\n'
            '    "programming_languages": [],\n'
            '    "frameworks": [],\n'
            '    "databases": [],\n'
            '    "cloud_devops": [],\n'
            '    "tools": []\n'
            "  }\n"
            "}\n"
        )

    def validate_recruiter_corrections(
        self,
        candidate_id: str,
        original_extraction: dict[str, Any],
        recruiter_corrected: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = self._correction_validation_prompt(
            candidate_id, original_extraction, recruiter_corrected
        )
        response = self._call_llm(prompt, task="correction_validation")
        data = self._parse_json(response.content, expect_array=False)
        if isinstance(data, dict):
            return data
        return {
            "candidate_id": candidate_id,
            "fields_corrected": [],
            "correction_count": 0,
            "accuracy_score": 0,
        }

    def _correction_validation_prompt(
        self,
        candidate_id: str,
        original_extraction: dict[str, Any],
        recruiter_corrected: dict[str, Any],
    ) -> str:
        return self._base_system_prompt + (
            "You are validating recruiter-corrected resume data.\n\n"
            "Compare:\n"
            "1. Original LLM Extraction\n"
            "2. Recruiter Corrected Version\n\n"
            "Tasks:\n\n"
            "1. Accept recruiter corrections as ground truth.\n"
            "2. Identify fields corrected.\n"
            "3. Mark error categories.\n\n"
            "Return JSON:\n\n"
            "{\n"
            '  "candidate_id": "",\n'
            '  "fields_corrected": [\n'
            "    {\n"
            '      "field_name": "",\n'
            '      "original_value": "",\n'
            '      "corrected_value": "",\n'
            '      "error_type": "extraction | normalization | hallucination | missing"\n'
            "    }\n"
            "  ],\n"
            '  "correction_count": 0,\n'
            '  "accuracy_score": 0\n'
            "}\n\n"
            "Candidate ID:\n"
            f"{candidate_id}\n\n"
            "Original LLM Extraction:\n"
            f"{json.dumps(original_extraction, ensure_ascii=False)}\n\n"
            "Recruiter Corrected Version:\n"
            f"{json.dumps(recruiter_corrected, ensure_ascii=False)}\n"
        )

    def normalize_skills_with_taxonomy(
        self,
        taxonomy_json: dict[str, Any] | list[Any],
        skills_list: list[Any],
    ) -> dict[str, Any]:
        prompt = self._skill_taxonomy_prompt(taxonomy_json, skills_list)
        response = self._call_llm(prompt, task="skill_taxonomy_normalization")
        data = self._parse_json(response.content, expect_array=False)
        if isinstance(data, dict):
            return data
        return {
            "normalized_skills": [],
            "unclassified_skills": [],
            "confidence_score": 0,
        }

    def _skill_taxonomy_prompt(
        self,
        taxonomy_json: dict[str, Any] | list[Any],
        skills_list: list[Any],
    ) -> str:
        return self._base_system_prompt + (
            "You are a Skill & Education Normalization AI.\n\n"
            "Tasks:\n\n"
            "1. Map extracted skills to taxonomy master list.\n"
            "2. Merge synonyms.\n"
            "3. Remove duplicates.\n"
            '4. Keep unmapped skills in "unclassified".\n\n'
            "Taxonomy:\n"
            f"{json.dumps(taxonomy_json, ensure_ascii=False)}\n\n"
            "Extracted Skills:\n"
            f"{json.dumps(skills_list, ensure_ascii=False)}\n\n"
            "Return JSON:\n\n"
            "{\n"
            '  "normalized_skills": [],\n'
            '  "unclassified_skills": [],\n'
            '  "confidence_score": 0\n'
            "}\n"
        )

    def reprocess_with_taxonomy(
        self,
        resume_text: str,
        taxonomy_json: dict[str, Any] | list[Any],
    ) -> dict[str, Any]:
        prompt = self._reprocess_with_taxonomy_prompt(resume_text, taxonomy_json)
        response = self._call_llm(prompt, task="reprocess_with_taxonomy")
        data = self._parse_json(response.content, expect_array=False)
        if isinstance(data, dict):
            return data
        return {}

    def _reprocess_with_taxonomy_prompt(
        self,
        resume_text: str,
        taxonomy_json: dict[str, Any] | list[Any],
    ) -> str:
        return self._base_system_prompt + (
            "Reprocess the resume using updated taxonomy.\n\n"
            "Rules:\n\n"
            "1. Use taxonomy for normalization.\n"
            "2. Re-evaluate inferred skills.\n"
            "3. Improve certification recognition.\n"
            "4. Do not change personal info unless wrong.\n\n"
            "Resume Text:\n"
            f"\"\"\"\n{resume_text}\n\"\"\"\n\n"
            "Updated Taxonomy:\n"
            f"{json.dumps(taxonomy_json, ensure_ascii=False)}\n\n"
            "Return updated structured JSON in same schema.\n"
        )

    def evaluate_extraction_accuracy(
        self,
        original_extraction: dict[str, Any],
        corrected_ground_truth: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = self._evaluation_prompt(original_extraction, corrected_ground_truth)
        response = self._call_llm(prompt, task="evaluation_accuracy")
        data = self._parse_json(response.content, expect_array=False)
        if isinstance(data, dict):
            return data
        return {
            "personal_info_accuracy": 0,
            "skills_accuracy": 0,
            "experience_accuracy": 0,
            "education_accuracy": 0,
            "certifications_accuracy": 0,
            "overall_accuracy": 0,
            "confidence_score": 0,
            "improvement_suggestions": [],
        }

    def _evaluation_prompt(
        self,
        original_extraction: dict[str, Any],
        corrected_ground_truth: dict[str, Any],
    ) -> str:
        return self._base_system_prompt + (
            "You are an AI Evaluation Engine.\n\n"
            "Compare:\n\n"
            "1. Original Extraction\n"
            "2. Corrected Ground Truth\n\n"
            "Calculate:\n\n"
            "• Field accuracy\n"
            "• Section accuracy\n"
            "• Overall accuracy\n"
            "• Confidence score\n\n"
            "Return JSON:\n\n"
            "{\n"
            '  "personal_info_accuracy": 0,\n'
            '  "skills_accuracy": 0,\n'
            '  "experience_accuracy": 0,\n'
            '  "education_accuracy": 0,\n'
            '  "certifications_accuracy": 0,\n'
            '  "overall_accuracy": 0,\n'
            '  "confidence_score": 0,\n'
            '  "improvement_suggestions": []\n'
            "}\n\n"
            "Original Extraction:\n"
            f"{json.dumps(original_extraction, ensure_ascii=False)}\n\n"
            "Corrected Ground Truth:\n"
            f"{json.dumps(corrected_ground_truth, ensure_ascii=False)}\n"
        )

    def build_training_pair(
        self,
        resume_text: str,
        ground_truth_json: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = self._training_pair_prompt(resume_text, ground_truth_json)
        response = self._call_llm(prompt, task="training_pair")
        data = self._parse_json(response.content, expect_array=False)
        if isinstance(data, dict):
            return data
        return {"input_text": resume_text, "expected_output": ground_truth_json}

    def _training_pair_prompt(
        self,
        resume_text: str,
        ground_truth_json: dict[str, Any],
    ) -> str:
        return self._base_system_prompt + (
            "You are generating training data for Resume Parsing AI.\n\n"
            "Input:\n\n"
            "• Resume Text\n"
            "• Ground Truth JSON\n\n"
            "Task:\n\n"
            "Create structured training pair.\n\n"
            "Return JSON:\n\n"
            "{\n"
            '  "input_text": "",\n'
            '  "expected_output": {}\n'
            "}\n\n"
            "Resume Text:\n"
            f"\"\"\"\n{resume_text}\n\"\"\"\n\n"
            "Ground Truth JSON:\n"
            f"{json.dumps(ground_truth_json, ensure_ascii=False)}\n"
        )

    def classify_extraction_error(
        self,
        original_vs_corrected: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = self._error_classification_prompt(original_vs_corrected)
        response = self._call_llm(prompt, task="error_classification")
        data = self._parse_json(response.content, expect_array=False)
        if isinstance(data, dict):
            return data
        return {"error_type": "", "severity": "low", "fix_strategy": ""}

    def _error_classification_prompt(
        self,
        original_vs_corrected: dict[str, Any],
    ) -> str:
        return self._base_system_prompt + (
            "Classify extraction errors.\n\n"
            "Error Types:\n\n"
            "1. OCR Error\n"
            "2. Parsing Error\n"
            "3. Normalization Error\n"
            "4. Hallucination\n"
            "5. Missing Entity\n\n"
            "Input:\n"
            f"{json.dumps(original_vs_corrected, ensure_ascii=False)}\n\n"
            "Return JSON:\n\n"
            "{\n"
            '  "error_type": "",\n'
            '  "severity": "low | medium | high",\n'
            '  "fix_strategy": ""\n'
            "}\n"
        )

    def analyze_extraction_failure(
        self,
        resume_text: str,
        llm_output: dict[str, Any],
        prompt_used: str,
        token_count: int | None,
    ) -> dict[str, Any]:
        prompt = self._extraction_failure_prompt(
            resume_text, llm_output, prompt_used, token_count
        )
        response = self._call_llm(prompt, task="extraction_failure_analysis")
        data = self._parse_json(response.content, expect_array=False)
        if isinstance(data, dict):
            return data
        return {
            "text_length": len(resume_text or ""),
            "sections_detected": [],
            "sections_missing": [],
            "prompt_quality_score": 0,
            "schema_mapping_score": 0,
            "root_cause": "",
            "fix_steps": [],
        }

    def _extraction_failure_prompt(
        self,
        resume_text: str,
        llm_output: dict[str, Any],
        prompt_used: str,
        token_count: int | None,
    ) -> str:
        return self._base_system_prompt + (
            "Analyze why resume extraction returns only name and phone.\n\n"
            "Input:\n\n"
            "• Resume text\n"
            "• LLM output\n"
            "• Prompt used\n"
            "• Token count\n\n"
            "Tasks:\n\n"
            "1. Check if resume text is truncated.\n"
            "2. Detect missing sections in input.\n"
            "3. Validate prompt strength.\n"
            "4. Identify schema mapping failures.\n"
            "5. Detect hallucination filtering errors.\n\n"
            "Return:\n\n"
            "{\n"
            '  "text_length": 0,\n'
            '  "sections_detected": [],\n'
            '  "sections_missing": [],\n'
            '  "prompt_quality_score": 0,\n'
            '  "schema_mapping_score": 0,\n'
            '  "root_cause": "",\n'
            '  "fix_steps": []\n'
            "}\n\n"
            "Resume Text:\n"
            f"\"\"\"\n{resume_text}\n\"\"\"\n\n"
            "LLM Output:\n"
            f"{json.dumps(llm_output, ensure_ascii=False)}\n\n"
            "Prompt Used:\n"
            f"\"\"\"\n{prompt_used}\n\"\"\"\n\n"
            "Token Count:\n"
            f"{token_count if token_count is not None else 0}\n"
        )

    def _education_normalization_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + (
            "Extract and normalize education details.\n\n"
            "Instructions:\n\n"
            "1. Convert degree abbreviations:\n"
            "   - MS → Master of Science\n"
            "   - BTech → Bachelor of Technology\n\n"
            "2. Normalize university names.\n"
            "3. Extract GPA if present.\n"
            "4. Detect US vs Non-US universities.\n\n"
            "Text:\n"
            f"\"\"\"\n{text}\n\"\"\"\n\n"
            "Return JSON:\n"
            "{\n"
            '  "degree": "",\n'
            '  "field_of_study": "",\n'
            '  "university": "",\n'
            '  "country": "",\n'
            '  "graduation_year": "",\n'
            '  "gpa": ""\n'
            "}\n"
        )

    def _work_experience_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + (
            "Extract work experience.\n\n"
            "For each job extract:\n\n"
            "• Company Name\n"
            "• Job Title\n"
            "• Client Name (if applicable)\n"
            "• Start Date\n"
            "• End Date\n"
            "• Current Role\n"
            "• Location\n"
            "• Responsibilities\n"
            "• Technologies Used\n\n"
            "Instructions:\n\n"
            "1. Identify each company separately.\n"
            "2. Extract dates accurately.\n"
            "3. Detect current role.\n"
            "4. Extract technologies used.\n"
            "5. Maintain chronological order.\n\n"
            "Text:\n"
            f"\"\"\"\n{text}\n\"\"\"\n\n"
            "Return JSON array with:\n\n"
            "- company_name\n"
            "- job_title\n"
            "- client_name\n"
            "- start_date\n"
            "- end_date\n"
            "- is_current\n"
            "- location\n"
            "- technologies\n"
            "- responsibilities\n"
        )

    def _certifications_extraction_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + self._base_system_prompt + (
            "You are a resume certifications extractor.\n\n"
            "Return ONLY valid JSON. No markdown. No explanations.\n"
            "Do NOT hallucinate certifications. Extract only what is present.\n\n"
            "Text:\n"
            f"\"\"\"\n{text}\n\"\"\"\n\n"
            "Return a JSON array of objects with exactly these keys:\n\n"
            "[\n"
            "  {\n"
            '    "name": null,\n'
            '    "issuing_organization": null,\n'
            '    "issue_date": null,\n'
            '    "expiry_date": null,\n'
            '    "credential_id": null,\n'
            '    "is_active": null,\n'
            '    "confidence": 0.0\n'
            "  }\n"
            "]\n"
        )

    def _total_experience_prompt(self, structured_experience_json: str) -> str:
        return (
            "Calculate total experience.\n\n"
            "Instructions:\n\n"
            "1. Use employment dates.\n"
            "2. Avoid overlaps.\n"
            "3. Return years + months.\n\n"
            "Input:\n"
            f"{structured_experience_json}\n\n"
            "Return:\n\n"
            "{\n"
            '  "total_experience_years": "",\n'
            '  "total_experience_months": ""\n'
            "}\n"
        )

    def _extraction_confidence_prompt(self, payload: dict[str, Any]) -> str:
        return (
            "Evaluate extraction confidence.\n\n"
            "Score each section from 0–100:\n\n"
            "- Personal Info\n"
            "- Skills\n"
            "- Experience\n"
            "- Education\n"
            "- Certifications\n\n"
            "Consider:\n\n"
            "- Completeness\n"
            "- Clarity\n"
            "- Extraction certainty\n\n"
            "Return:\n\n"
            "{\n"
            '  "confidence_scores": {\n'
            '    "personal_info": 0,\n'
            '    "skills": 0,\n'
            '    "experience": 0,\n'
            '    "education": 0,\n'
            '    "certifications": 0\n'
            "    },\n"
            '  "overall_confidence": 0\n'
            "}\n\n"
            f"Extraction Data:\n{json.dumps(payload, ensure_ascii=False)}\n"
        )

    def _normalize_skills_prompt(self, skills_array: list[Any]) -> str:
        return (
            "Normalize and deduplicate skills.\n\n"
            "Input:\n"
            f"{json.dumps(skills_array, ensure_ascii=False)}\n\n"
            "Instructions:\n\n"
            "1. Merge synonyms.\n"
            "2. Convert to canonical names.\n"
            "3. Remove duplicates.\n"
            "4. Preserve seniority relevance.\n\n"
            "Return:\n\n"
            "{\n"
            '  "normalized_skills": []\n'
            "}\n"
        )

    def _verification_prompt(self, resume_text: str, extracted_payload: dict[str, Any]) -> str:
        return (
            "Verify extracted data against resume text.\n\n"
            "Instructions:\n\n"
            "1. Remove any field not present in the resume.\n"
            "2. Flag inferred vs explicit skills.\n"
            "3. Ensure dates and companies exist in text.\n\n"
            "Return validated JSON only.\n\n"
            "Resume Text:\n"
            f"\"\"\"\n{resume_text}\n\"\"\"\n\n"
            "Extracted Data:\n"
            f"{json.dumps(extracted_payload, ensure_ascii=False)}\n"
        )

    @staticmethod
    def _merge_personal_info(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        merged = dict(base)
        for key, value in incoming.items():
            if isinstance(value, list):
                existing = merged.get(key, [])
                if not isinstance(existing, list):
                    existing = []
                merged[key] = list({*existing, *value})
            elif isinstance(value, dict):
                existing = merged.get(key, {})
                if not isinstance(existing, dict):
                    existing = {}
                merged[key] = {**existing, **{k: v for k, v in value.items() if v}}
            else:
                if value not in (None, "", []):
                    merged[key] = value
        return merged

    def _merge_structured_resume(self, partials: list[dict[str, Any]]) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for entry in partials:
            if not isinstance(entry, dict):
                continue
            for key, value in entry.items():
                if key not in merged or merged[key] in (None, "", [], {}):
                    merged[key] = value
                elif isinstance(value, list) and isinstance(merged.get(key), list):
                    merged[key] = self._unique_list(merged[key] + value)
                elif isinstance(value, dict) and isinstance(merged.get(key), dict):
                    merged[key] = {**merged[key], **{k: v for k, v in value.items() if v}}
        return merged

    def _chunk_text(self, text: str) -> list[str]:
        limit = self.settings.LLM_MAX_CHARS
        chunk_size = self.settings.LLM_CHUNK_CHARS
        overlap = self.settings.LLM_CHUNK_OVERLAP
        if len(text) <= limit:
            return [text]

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}" if current else paragraph
            if len(candidate) <= chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current)
            if len(paragraph) <= chunk_size:
                current = paragraph
            else:
                start = 0
                while start < len(paragraph):
                    end = min(start + chunk_size, len(paragraph))
                    chunks.append(paragraph[start:end])
                    start = end - overlap if overlap and end < len(paragraph) else end
                current = ""
        if current:
            chunks.append(current)
        return chunks or [text]

    def _merge_resume_intelligence(
        self, partials: list[dict[str, Any]]
    ) -> dict[str, Any]:
        merged: dict[str, Any] = {
            "candidate_information": {},
            "professional_summary": {},
            "technical_skills": {},
            "project_client_experience": [],
            "architecture_enterprise_experience": [],
            "cloud_devops_experience": {},
            "education": [],
            "certifications": [],
            "domain_experience": [],
        }

        def first_non_empty(value: Any, existing: Any) -> Any:
            return existing if existing not in (None, "", [], {}) else value

        def merge_list(target: list[Any], items: Any) -> None:
            if items is None:
                return
            if isinstance(items, list):
                target.extend(items)
            else:
                target.append(items)

        def merge_dict(target: dict[str, Any], source: Any) -> None:
            if not isinstance(source, dict):
                return
            for key, value in source.items():
                if isinstance(value, dict) and isinstance(target.get(key), dict):
                    merge_dict(target[key], value)
                elif isinstance(value, list):
                    existing = target.get(key, [])
                    if not isinstance(existing, list):
                        existing = [existing]
                    target[key] = self._unique_list(existing + value)
                else:
                    target[key] = first_non_empty(value, target.get(key))

        for entry in partials:
            if not isinstance(entry, dict):
                continue
            candidate_info = (
                entry.get("candidate_information")
                or entry.get("candidate_info")
                or entry.get("candidate")
            )
            merge_dict(merged["candidate_information"], candidate_info)

            professional = entry.get("professional_summary") or {}
            if isinstance(professional, dict):
                existing_years = merged["professional_summary"].get("years_of_experience")
                new_years = professional.get("years_of_experience")
                try:
                    if new_years is not None:
                        new_years_val = float(new_years)
                        if existing_years is None or new_years_val > float(existing_years):
                            merged["professional_summary"]["years_of_experience"] = new_years_val
                except (TypeError, ValueError):
                    pass
                for key in ("primary_role", "seniority_level"):
                    merged["professional_summary"][key] = first_non_empty(
                        professional.get(key),
                        merged["professional_summary"].get(key),
                    )

            technical = entry.get("technical_skills")
            if isinstance(technical, dict):
                for key, value in technical.items():
                    existing = merged["technical_skills"].get(key, [])
                    merged["technical_skills"][key] = self._unique_list(
                        self._coerce_list(existing) + self._coerce_list(value)
                    )

            merge_list(
                merged["project_client_experience"],
                entry.get("project_client_experience")
                or entry.get("client_experience")
                or entry.get("projects"),
            )

            merge_list(
                merged["architecture_enterprise_experience"],
                entry.get("architecture_enterprise_experience")
                or entry.get("architecture_experience"),
            )

            merge_dict(
                merged["cloud_devops_experience"],
                entry.get("cloud_devops_experience") or entry.get("cloud_devops"),
            )

            merge_list(merged["education"], entry.get("education"))
            merge_list(merged["certifications"], entry.get("certifications"))
            merge_list(merged["domain_experience"], entry.get("domain_experience"))

        merged["project_client_experience"] = self._unique_list(
            merged["project_client_experience"]
        )
        merged["architecture_enterprise_experience"] = self._unique_list(
            merged["architecture_enterprise_experience"]
        )
        merged["domain_experience"] = self._unique_list(merged["domain_experience"])
        return merged

    def _coerce_list(self, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _unique_list(self, values: list[Any]) -> list[Any]:
        seen: set[str] = set()
        unique: list[Any] = []
        for item in values:
            marker = json.dumps(item, sort_keys=True) if isinstance(item, dict) else str(item)
            if marker in seen:
                continue
            seen.add(marker)
            unique.append(item)
        return unique

    def extract_work_experience(self, text: str) -> list[dict[str, Any]]:
        prompt = (
            "Extract work experience from this resume section. "
            "Return JSON array of objects with: company_name, client_name, job_title, "
            "start_date, end_date, is_current, location, responsibilities (array). "
            f"Here's the text:\n{text}"
        )
        response = self._call_llm(prompt, task="work_experience")
        data = self._parse_json(response.content, expect_array=True)
        if isinstance(data, dict):
            return [data]
        return data or []

    def infer_skills(self, text: str) -> list[dict[str, Any]]:
        prompt = (
            "Analyze these job descriptions and extract technical skills, tools, "
            "and technologies mentioned. Also infer related skills. "
            "Return JSON array of {skill_name, category, proficiency_level, evidence}. "
            f"Text:\n{text}"
        )
        response = self._call_llm(prompt, task="skill_inference")
        data = self._parse_json(response.content, expect_array=True)
        return data or []

    def normalize_titles_and_companies(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "Normalize these company names and job titles to standard formats. "
            f"Input: {json.dumps(raw_data, ensure_ascii=False)}. "
            "Return JSON with normalized values."
        )
        response = self._call_llm(prompt, task="normalization")
        data = self._parse_json(response.content, expect_array=False)
        return data or {}

    def _call_llm(self, prompt: str, task: str) -> LLMResponse:
        provider = (self.settings.LLM_PROVIDER or "").lower()
        if provider == "none":
            return LLMResponse(content="{}")

        cache_key = self._cache_key(prompt, task)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        LLM_CACHE_MISSES.inc()
        self._enforce_rate_limit()

        if provider != "local":
            raise RuntimeError(f"Unsupported LLM_PROVIDER: {self.settings.LLM_PROVIDER}")

        primary = self.settings.LOCAL_LLM_MODEL
        response = self._call_local(prompt, primary, task)
        if not response and self.settings.LOCAL_LLM_FALLBACK_MODEL:
            response = self._call_local(prompt, self.settings.LOCAL_LLM_FALLBACK_MODEL, task)

        if not response:
            if self.settings.ENVIRONMENT.lower() in {"development", "local"} or (
                self.settings.LLM_PROVIDER == "local"
            ):
                logger.warning("LLM unavailable; returning empty response")
                return LLMResponse(content="{}")
            raise RuntimeError("LLM request failed")

        self._set_cached(cache_key, response)
        return response

    def _call_local(self, prompt: str, model: str | None, task: str) -> LLMResponse | None:
        if not model:
            return None
        options: dict[str, Any] = {"temperature": self.settings.OLLAMA_TEMPERATURE}
        if self.settings.OLLAMA_NUM_CTX is not None:
            options["num_ctx"] = self.settings.OLLAMA_NUM_CTX
        if self.settings.OLLAMA_NUM_BATCH is not None:
            options["num_batch"] = self.settings.OLLAMA_NUM_BATCH
        if self.settings.OLLAMA_NUM_THREAD is not None:
            options["num_thread"] = self.settings.OLLAMA_NUM_THREAD
        if self.settings.OLLAMA_NUM_GPU is not None:
            options["num_gpu"] = self.settings.OLLAMA_NUM_GPU

        payload = {
            "model": model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": options,
        }
        if self.settings.OLLAMA_KEEP_ALIVE:
            payload["keep_alive"] = self.settings.OLLAMA_KEEP_ALIVE

        attempts = self.settings.LLM_MAX_RETRIES + 1
        for attempt in range(1, attempts + 1):
            try:
                response = httpx.post(
                    f"{self.settings.LOCAL_LLM_BASE_URL}/api/generate",
                    json=payload,
                    timeout=self.settings.LLM_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("response", "")
                tokens = data.get("eval_count")
                self._track_cost(task="local", tokens=tokens, model=model)
                return LLMResponse(content=content, tokens=tokens, model=model)
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Local LLM call failed",
                    extra={"attempt": attempt, "max_attempts": attempts},
                )
                if attempt < attempts:
                    time.sleep(1.5 * attempt)
                    continue
                return None

    def _parse_json(self, content: str, expect_array: bool) -> Any:
        extracted = self._extract_json_block(content)
        if extracted is None:
            if expect_array:
                start = content.find("[")
                end = content.rfind("]")
                if start != -1 and end != -1 and end > start:
                    extracted = content[start : end + 1]
            if extracted is None:
                extracted = content
        try:
            parsed = json.loads(extracted)
            if isinstance(parsed, str):
                parsed = json.loads(parsed)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Malformed LLM JSON response")
            return [] if expect_array else {}

        if expect_array and not isinstance(parsed, list):
            return [parsed] if isinstance(parsed, dict) else []
        if not expect_array and not isinstance(parsed, dict):
            return {}
        return parsed

    @staticmethod
    def _extract_json_block(text: str) -> str | None:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return None

    def _enforce_rate_limit(self) -> None:
        if self.settings.LLM_PROVIDER == "local":
            return
        limit = self.settings.LLM_RATE_LIMIT_PER_MINUTE
        now = time.time()
        window_start = now - 60
        self._rate_timestamps = [t for t in self._rate_timestamps if t >= window_start]
        if len(self._rate_timestamps) >= limit:
            raise RuntimeError("LLM rate limit exceeded")
        self._rate_timestamps.append(now)

    def _track_cost(self, task: str, tokens: int | None, model: str) -> None:
        if tokens is None:
            return
        logger.info(
            "LLM usage",
            extra={"task": task, "tokens": tokens, "model": model},
        )

    def _cache_key(self, prompt: str, task: str, model: str | None = None) -> str:
        model_part = model or self.settings.LOCAL_LLM_MODEL or "default"
        payload = f"{model_part}:{task}:{prompt}".encode("utf-8")
        h = hashlib.sha256(payload).hexdigest()[:24]
        return f"llm_cache:{h}"

    def _get_cached(self, key: str) -> LLMResponse | None:
        ttl = self.settings.LLM_CACHE_TTL_SECONDS
        client = get_redis_client()
        if client:
            try:
                cached = client.get(key)
                if cached:
                    LLM_CACHE_HITS.inc()
                    data = json.loads(cached)
                    return LLMResponse(
                        content=data.get("content", "{}"),
                        tokens=data.get("tokens"),
                        model=data.get("model"),
                    )
            except Exception:  # noqa: BLE001
                pass
        entry = self._cache.get(key)
        if not entry:
            return None
        timestamp, response = entry
        if time.time() - timestamp > ttl:
            self._cache.pop(key, None)
            return None
        LLM_CACHE_HITS.inc()
        return response

    def _set_cached(self, key: str, response: LLMResponse) -> None:
        client = get_redis_client()
        if client:
            try:
                data = {
                    "content": response.content,
                    "tokens": response.tokens,
                    "model": response.model,
                }
                client.setex(key, self.settings.LLM_CACHE_TTL_SECONDS, json.dumps(data))
                return
            except Exception:  # noqa: BLE001
                pass
        self._cache[key] = (time.time(), response)
