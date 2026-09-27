import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

print("MAIL_USERNAME:", settings.MAIL_USERNAME)
print("MAIL_FROM:", settings.MAIL_FROM)
print("MAIL_SERVER:", settings.MAIL_SERVER)
print("MAIL_PORT:", settings.MAIL_PORT)
print("MAIL_PASSWORD length:", len(settings.MAIL_PASSWORD))
print("MAIL_PASSWORD (oculto):", settings.MAIL_PASSWORD[:4] + "****")

msg = MIMEText("Prueba de correo desde FlowOS")
msg["Subject"] = "Prueba FlowOS"
msg["From"] = settings.MAIL_FROM
msg["To"] = settings.MAIL_FROM

try:
    print("\nConectando...")
    server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=30)
    server.set_debuglevel(1)  # muestra el diálogo SMTP
    print("EHLO...")
    server.ehlo()
    print("STARTTLS...")
    server.starttls()
    server.ehlo()
    print("Login...")
    server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
    print("Enviando...")
    server.sendmail(settings.MAIL_FROM, settings.MAIL_FROM, msg.as_string())
    server.quit()
    print("\n✅ Correo enviado correctamente")
except Exception as e:
    print("\n❌ Error:", type(e).__name__, e)