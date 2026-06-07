from sqlalchemy.orm import Session

from app.models.system_setting import SystemSetting


class SystemSettingService:
    DEFAULT_SETTINGS = [
        {
            "key": "llm_model",
            "category": "ai",
            "value": "gemma-4-27b-or-31b-provider-model",
            "description": "Model name used by the AI provider. Keep the provider free-tier RPM limit in mind.",
        },
        {
            "key": "llm_requests_per_minute",
            "category": "ai",
            "value": 12,
            "description": "Configured below the 15 RPM provider limit to avoid throttling.",
        },
        {
            "key": "prompt_resume_generation",
            "category": "prompts",
            "value": "Generate a concise, ATS-friendly resume tailored to the target role without inventing facts.",
            "description": "Admin-editable prompt guidance for resume generation.",
        },
        {
            "key": "prompt_jd_parser",
            "category": "prompts",
            "value": "Extract role, skills, experience, education, location, salary, responsibilities, keywords, and tech stack.",
            "description": "Admin-editable prompt guidance for JD understanding.",
        },
        {
            "key": "prompt_matching",
            "category": "prompts",
            "value": "Score candidate and job fit across skills, experience, projects, location, salary, education, and keywords.",
            "description": "Admin-editable prompt guidance for matching.",
        },
        {
            "key": "n8n_email_intake_webhook",
            "category": "integrations",
            "value": "",
            "description": "n8n webhook URL for email intake profile building.",
        },
        {
            "key": "n8n_job_discovery_webhook",
            "category": "integrations",
            "value": "",
            "description": "n8n webhook URL for safe job discovery ingestion.",
        },
        {
            "key": "support_email",
            "category": "operations",
            "value": "",
            "description": "Support email shown or used by operations workflows.",
        },
    ]

    def ensure_defaults(self, db: Session):
        existing_keys = {key for (key,) in db.query(SystemSetting.key).all()}
        created = []
        for item in self.DEFAULT_SETTINGS:
            if item["key"] in existing_keys:
                continue
            setting = SystemSetting(**item)
            db.add(setting)
            created.append(setting)
        if created:
            db.commit()
        return created

    def list(self, db: Session, category: str | None = None):
        self.ensure_defaults(db)
        query = db.query(SystemSetting)
        if category:
            query = query.filter(SystemSetting.category == category)
        return query.order_by(SystemSetting.category.asc(), SystemSetting.key.asc()).all()

    def update(self, db: Session, key: str, value, description: str | None, updated_by_user_id: int):
        self.ensure_defaults(db)
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if not setting:
            return None
        setting.value = value
        if description is not None:
            setting.description = description
        setting.updated_by_user_id = updated_by_user_id
        db.commit()
        db.refresh(setting)
        return setting
