"""
utility functions used in sending of emails within the application. currently
these integrate with a 3rd party appnamed "Resend" to send said emails. Was
previously using basic gmail smtp+app passwords for this functionality, but it
does not allow adding custom domain to senders address, hence made the switch.

contains 2 main functions:
    - send_email
    - send_password_reset_email
"""

from email.message import EmailMessage

import aiosmtplib

from app.config import settings
from app.main import templates


async def send_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: str | None = None,
):
    """
    function for sending emails within the application. this can be called in
    other fucntions repeatedlyandas long as the needed parameters are passed,
    it succesfully sends the emails.

    parameters are:
        - to_email: where email is going
        - subject: subject fo the email being sent
        - plain_text: plain text content of email, for email clients that dont
          read html based content, e.g cli-based clients
        - html_content: emal formatted as html, for email clients that accept
          html content
    """
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(plain_text)

    # if html accepted, use that
    if html_content:
        message.add_alternative(html_content, subtype="html")

    # send the email
    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username if settings.mail_username else None,
        password=settings.mail_password.get_secret_value() or None,
        start_tls=settings.mail_use_tls,
    )


async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    """
    this function is used for sending password reset emails. its used in tandem
    with the "send_email" defined above, whereby the needed values are passed
    into the fucntion as it is called

    it parameters are:
        - to_email: who the email is being sent to
        - username: username of the user receiving the email
        - token: single use token to verify the user identity and session for
          security

    NOTE:
    - this is not a REST-based endpoint with "GET"/"POST" hence we cannot
      return a TemplateResponse. Instead, we render it with the
      ".env.get_template" that allows us to input our placeholders in place,
      making it dynamic.
    - plain_text string is defined as a fallback for email clients that do not
      render html pages, mostly CLI-based ones orfor users who have disabled
      that
    """

    reset_url = f"{settings.frontend_url}/auth/reset-password?token={token}"

    template = templates.env.get_template("emails/password_reset.html")
    html_content = template.render(reset_url=reset_url, username=username)

    plain_text = f"""
    Hi {username},

    You requested to reset your password. Click the link below to set a new
    password:

    {reset_url}

    This link will expire in {settings.reset_expiration_minutes} minutes.

    If you did not request this, you can safely ignore this email.

    Best Regards,
    The FastAPI Blog Team.
    """

    await send_email(
        to_email=to_email,
        subject="Reset Your Password - FastAPI Blog",
        plain_text=plain_text,
        html_content=html_content,
    )
