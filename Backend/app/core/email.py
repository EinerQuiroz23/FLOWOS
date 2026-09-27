import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def enviar_codigo_recuperacion(email_destino: str, codigo: str) -> None:
    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = "Código de recuperación - FlowOS"
    mensaje["From"] = settings.MAIL_FROM
    mensaje["To"] = email_destino

    texto = f"""
Hola,

Recibimos una solicitud para restablecer la contraseña de tu cuenta en FlowOS.

Tu código de verificación es: {codigo}

Este código expira en {settings.RESET_TOKEN_EXPIRE_MINUTES} minutos.

Si no solicitaste este cambio, puedes ignorar este correo.

— Equipo FlowOS
"""

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Recuperación de contraseña - FLOWOS</h2>
        <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
        <p style="font-size: 24px; font-weight: bold; letter-spacing: 4px;">{codigo}</p>
        <p>Este código expira en <strong>{settings.RESET_TOKEN_EXPIRE_MINUTES} minutos</strong>.</p>
        <p>Si no solicitaste este cambio, ignora este correo.</p>
        <br>
        <p>— Equipo FlowOS</p>
      </body>
    </html>
    """

    mensaje.attach(MIMEText(texto, "plain"))
    mensaje.attach(MIMEText(html, "html"))

    server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=30)
    try:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.sendmail(
            settings.MAIL_FROM,
            email_destino,
            mensaje.as_string()
        )
    finally:
        server.quit()