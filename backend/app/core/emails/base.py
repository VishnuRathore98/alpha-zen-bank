from jinja2 import Environment, FileSystemLoader
from backend.app.core.emails.config import TEMPLATES_DIR
from backend.app.core.emails.tasks import send_email_task
from backend.app.core.loguru_logging import get_logger


logger = get_logger()

email_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=True
)

class EmailTemplate:
    template_name: str
    template_name_plain: str
    subject: str

    @classmethod
    async def send_email(
        cls,
        email_to: str|list[str],
        context: dict,
        subject_override: str | None = None,
    ) -> None:
        try:
            recipients_list = [email_to] is isinstance(email_to, str) else email_to
            if not cls.template_name or not cls.template_name_plain:
                raise ValueError("Both HTML and plain text email templates are required")
            html_template = email_env.get_template(cls.template_name)
            plain_template = email_env.get_template(cls.template_name_plain)

            html_template = html_template.render(**context)
            plain_template = plain_template.render(**context)

            

        except Exception as e:
            pass
