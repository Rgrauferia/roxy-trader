# alerts.py – módulo de notificaciones por correo

import smtplib
from email.mime.text import MIMEText

# === CONFIGURA ESTOS DATOS ===
EMAIL_ORIGEN = "roxy@grau360.com"           # Correo desde el cual se envía
EMAIL_DESTINO = "tucorreo@gmail.com"        # Correo que recibirá las alertas
SMTP_SERVER = "mail.privateemail.com"       # Servidor SMTP
SMTP_PORT = 465                              # Puerto para SSL
EMAIL_PASSWORD = "AQUÍ_TU_PASSWORD"         # Contraseña del correo de envío

def enviar_alerta(mensaje):
    try:
        msg = MIMEText(mensaje)
        msg["Subject"] = "📢 Alerta de Roxy Trader"
        msg["From"] = EMAIL_ORIGEN
        msg["To"] = EMAIL_DESTINO

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_ORIGEN, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ORIGEN, EMAIL_DESTINO, msg.as_string())
        server.quit()

        print("✅ Alerta enviada por correo.")
    except Exception as e:
        print(f"⚠️ Error al enviar alerta: {e}")
