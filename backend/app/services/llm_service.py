import json
import re
from typing import Any, Dict, List

from app.core.config import settings
from app.schemas.profile import CandidateProfile

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None


class ProfileExtractor:
    PROMPT = (
        "Extract the resume profile into JSON with the following fields: "
        "full_name, email, phone, summary, education, experience, projects, skills, certifications, links, preferences. "
        "Return valid JSON only. Use arrays for lists and objects for entries. "
        "If a field is not present, return an empty array or null as appropriate."
    )

    def extract_profile(self, text: str) -> CandidateProfile:
        if settings.gemini_api_key and genai:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                response = genai.chat.completions.create(
                    model=settings.gemini_model,
                    messages=[
                        {"author": "system", "content": "You are a resume profile extraction assistant."},
                        {"author": "user", "content": f"{self.PROMPT}\n\nResume:\n{text}"},
                    ],
                    temperature=0.1,
                )
                content = self._extract_gemini_text(response)
                payload = self._load_json(content)
                return CandidateProfile(**payload)
            except Exception:
                pass

        if settings.openai_api_key and openai:
            try:
                openai.api_key = settings.openai_api_key
                response = openai.ChatCompletion.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": "You are a resume profile extraction assistant."},
                        {"role": "user", "content": f"{self.PROMPT}\n\nResume:\n{text}"},
                    ],
                    temperature=0.1,
                )
                content = response.choices[0].message.content
                payload = self._load_json(content)
                return CandidateProfile(**payload)
            except Exception:
                pass

        return self._fallback_extract(text)

    def _extract_gemini_text(self, response: Any) -> str:
        if hasattr(response, "last") and response.last:
            return getattr(response.last, "content", response.last)
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                return candidate.content[0].text
        if isinstance(response, dict):
            return response.get("output", {}).get("content", [{}])[0].get("text", "")
        return str(response)

    def _load_json(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            cleaned = self._extract_json_block(content)
            return json.loads(cleaned)

    def _extract_json_block(self, content: str) -> str:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("Unable to extract JSON from model response")
        return match.group(0)

    def _fallback_extract(self, text: str) -> CandidateProfile:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        email = self._find_email(text)
        phone = self._find_phone(text)
        full_name = lines[0] if lines else None
        summary = lines[1] if len(lines) > 1 else None
        return CandidateProfile(
            full_name=full_name,
            email=email,
            phone=phone,
            summary=summary,
            skills=[],
            education=[],
            experience=[],
            projects=[],
            certifications=[],
            links=[],
            preferences=None,
        )

    def _find_email(self, text: str) -> Any:
        match = re.search(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}", text)
        return match.group(0) if match else None

    def _find_phone(self, text: str) -> Any:
        match = re.search(r"\+?[0-9][0-9\-\s()]{7,}[0-9]", text)
        return match.group(0) if match else None


class JobDescriptionExtractor:
    PROMPT = (
        "Extract the job description into JSON with the following fields: "
        "title, company, location, description, requirements, skills, responsibilities, employment_type, experience_level. "
        "Return valid JSON only. Use arrays for requirements, skills, and responsibilities. "
        "If a field is not present, return an empty array or null as appropriate."
    )

    def extract_job(self, text: str) -> Dict[str, Any]:
        if settings.gemini_api_key and genai:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                response = genai.chat.completions.create(
                    model=settings.gemini_model,
                    messages=[
                        {"author": "system", "content": "You are a job description parser."},
                        {"author": "user", "content": f"{self.PROMPT}\n\nJob Description:\n{text}"},
                    ],
                    temperature=0.1,
                )
                content = self._extract_gemini_text(response)
                payload = self._load_json(content)
                return self._normalize_payload(payload, text)
            except Exception:
                pass

        if settings.openai_api_key and openai:
            try:
                openai.api_key = settings.openai_api_key
                response = openai.ChatCompletion.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": "You are a job description parser."},
                        {"role": "user", "content": f"{self.PROMPT}\n\nJob Description:\n{text}"},
                    ],
                    temperature=0.1,
                )
                content = response.choices[0].message.content
                payload = self._load_json(content)
                return self._normalize_payload(payload, text)
            except Exception:
                pass

        return self._fallback_extract(text)

    def _normalize_payload(self, payload: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        data = {k: payload.get(k) for k in ["title", "company", "location", "description"]}
        data["raw_text"] = raw_text
        structured = {
            "requirements": payload.get("requirements", []),
            "skills": payload.get("skills", []),
            "responsibilities": payload.get("responsibilities", []),
            "employment_type": payload.get("employment_type"),
            "experience_level": payload.get("experience_level"),
        }
        data["structured_data"] = structured
        return data

    def _fallback_extract(self, text: str) -> Dict[str, Any]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        title = lines[0] if lines else ""
        company = lines[1] if len(lines) > 1 else None
        location = None
        description_lines = []
        requirements = []
        skills = []
        responsibilities = []
        employment_type = None
        experience_level = None

        for line in lines[2:]:
            lower = line.lower()
            if "location" in lower and ":" in line:
                location = line.split(":", 1)[1].strip()
                continue
            if any(keyword in lower for keyword in ["requirements", "qualifications", "must have"]):
                requirements.extend(self._extract_list_items(line))
                continue
            if any(keyword in lower for keyword in ["skills", "technologies", "experience with"]):
                skills.extend(self._extract_list_items(line))
                continue
            if any(keyword in lower for keyword in ["responsibilities", "responsible for", "you will"]):
                responsibilities.extend(self._extract_list_items(line))
                continue
            if any(keyword in lower for keyword in ["full-time", "part-time", "contract", "internship"]):
                employment_type = next((word for word in line.split() if word.lower() in ["full-time", "part-time", "contract", "internship"]), employment_type)
            if any(keyword in lower for keyword in ["senior", "junior", "mid", "lead"]):
                experience_level = next((word for word in line.split() if word.lower() in ["senior", "junior", "mid", "lead"]), experience_level)
            description_lines.append(line)

        if not description_lines:
            description_lines = lines[2:]

        return {
            "title": title or "Unknown Role",
            "company": company,
            "location": location,
            "description": " ".join(description_lines).strip(),
            "raw_text": text,
            "structured_data": {
                "requirements": list({item for item in requirements if item}),
                "skills": list({skill.lower() for skill in skills if skill}),
                "responsibilities": list({item for item in responsibilities if item}),
                "employment_type": employment_type,
                "experience_level": experience_level,
            },
        }

    def _extract_list_items(self, line: str) -> List[str]:
        if "-" in line:
            items = [item.strip() for item in line.split("-") if item.strip()]
        elif "," in line:
            items = [item.strip() for item in line.split(",") if item.strip()]
        else:
            items = [line.split(":", 1)[-1].strip()]
        return items
