import logging

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

def send_template_email(subject, template, context, to):
    """
    Send email from template to a destiantion. The parameter
    template must have the html and the txt file
    """
    
    text_content = render_to_string(f"emails/{template}.txt", context)
    html_content = render_to_string(f"emails/{template}.html", context)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        None,
        [to],
    )

    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
        logging.info(f"Mail template={template} Sent")
    except Exception as e:
        logging.error(f"[Mail] Error sending template={template}: {e}")
        raise