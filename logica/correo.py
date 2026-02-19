# Módulo: logica/correo.py

import imaplib
import smtplib
import email
import ssl
import os
from email.mime.text import MIMEText
from email.header import decode_header
from dotenv import load_dotenv, set_key

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')


class CorreoClient:
    """Cliente de correo IMAP/SMTP con persistencia de credenciales."""

    # Puertos por defecto según modo de cifrado
    PUERTOS = {
        "none":     {"imap": 143, "smtp": 25},
        "ssl":      {"imap": 993, "smtp": 465},
        "starttls": {"imap": 143, "smtp": 587},
    }

    def __init__(self):
        self.imap = None
        self.server = ""
        self.imap_port = 143
        self.smtp_port = 25
        self.user = ""
        self.password = ""
        self.security = "none"  # "none", "ssl", "starttls"

    # ------------------------------------------------------------------
    # Configuración persistente (.env)
    # ------------------------------------------------------------------

    def cargar_config(self):
        """Lee credenciales del archivo .env. Devuelve dict con los valores."""
        load_dotenv(ENV_PATH, override=True)
        return {
            "server": os.getenv("MAIL_SERVER", ""),
            "imap_port": os.getenv("MAIL_IMAP_PORT", "143"),
            "smtp_port": os.getenv("MAIL_SMTP_PORT", "25"),
            "user": os.getenv("MAIL_USER", ""),
            "password": os.getenv("MAIL_PASSWORD", ""),
            "security": os.getenv("MAIL_SECURITY", "none"),
        }

    def guardar_config(self, server, imap_port, smtp_port, user, password, security):
        """Escribe credenciales al archivo .env."""
        if not os.path.exists(ENV_PATH):
            with open(ENV_PATH, "w") as f:
                f.write("")
        set_key(ENV_PATH, "MAIL_SERVER", server)
        set_key(ENV_PATH, "MAIL_IMAP_PORT", str(imap_port))
        set_key(ENV_PATH, "MAIL_SMTP_PORT", str(smtp_port))
        set_key(ENV_PATH, "MAIL_USER", user)
        set_key(ENV_PATH, "MAIL_PASSWORD", password)
        set_key(ENV_PATH, "MAIL_SECURITY", security)

    # ------------------------------------------------------------------
    # Conexión IMAP
    # ------------------------------------------------------------------

    def conectar(self, server, imap_port, user, password, security="none"):
        """Conecta al servidor IMAP y hace login.
        security: "none", "ssl" o "starttls"
        """
        self.server = server
        self.imap_port = int(imap_port)
        self.user = user
        self.password = password
        self.security = security

        if security == "ssl":
            ctx = ssl.create_default_context()
            self.imap = imaplib.IMAP4_SSL(server, self.imap_port, ssl_context=ctx)
        elif security == "starttls":
            self.imap = imaplib.IMAP4(server, self.imap_port)
            self.imap.starttls(ssl.create_default_context())
        else:
            self.imap = imaplib.IMAP4(server, self.imap_port)

        self.imap.login(user, password)

    def desconectar(self):
        """Cierra la conexión IMAP."""
        if self.imap:
            try:
                self.imap.logout()
            except Exception:
                pass
            self.imap = None

    # ------------------------------------------------------------------
    # Bandeja de entrada
    # ------------------------------------------------------------------

    def obtener_bandeja(self):
        """Lista correos del INBOX. Devuelve lista de dicts con uid, de, asunto, fecha."""
        self.imap.select("INBOX")
        status, data = self.imap.uid("search", None, "ALL")
        if status != "OK":
            return []

        uids = data[0].split()
        correos = []

        for uid in reversed(uids[-100:]):  # Últimos 100, más recientes primero
            status, msg_data = self.imap.uid("fetch", uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
            if status != "OK" or not msg_data[0]:
                continue

            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            de = self._decode_header(msg.get("From", ""))
            asunto = self._decode_header(msg.get("Subject", "(Sin asunto)"))
            fecha = msg.get("Date", "")

            correos.append({
                "uid": uid.decode(),
                "de": de,
                "asunto": asunto,
                "fecha": fecha,
            })

        return correos

    def leer_correo(self, uid):
        """Lee el contenido completo de un correo por UID. Devuelve texto plano."""
        self.imap.select("INBOX")
        status, msg_data = self.imap.uid("fetch", uid.encode(), "(RFC822)")
        if status != "OK" or not msg_data[0]:
            return "(No se pudo leer el correo)"

        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                if ct == "text/plain":
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    body += payload.decode(charset, errors="replace")
        else:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or "utf-8"
            body = payload.decode(charset, errors="replace")

        return body if body else "(Correo sin contenido de texto)"

    # ------------------------------------------------------------------
    # Envío SMTP
    # ------------------------------------------------------------------

    def enviar_correo(self, smtp_server, smtp_port, from_addr, password, to, subject, body, security="none"):
        """Envía un email vía SMTP.
        security: "none", "ssl" o "starttls"
        """
        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = from_addr
        msg["To"] = to
        msg["Subject"] = subject

        if security == "ssl":
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, int(smtp_port), context=ctx) as smtp:
                smtp.ehlo()
                if smtp.has_extn("AUTH") and password:
                    smtp.login(from_addr, password)
                smtp.send_message(msg)
        elif security == "starttls":
            with smtplib.SMTP(smtp_server, int(smtp_port)) as smtp:
                smtp.ehlo()
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
                if smtp.has_extn("AUTH") and password:
                    smtp.login(from_addr, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, int(smtp_port)) as smtp:
                smtp.ehlo()
                if smtp.has_extn("AUTH") and password:
                    try:
                        smtp.login(from_addr, password)
                    except smtplib.SMTPAuthenticationError:
                        pass  # Servidor interno: anuncia AUTH pero no lo requiere
                smtp.send_message(msg)

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    @staticmethod
    def _decode_header(value):
        """Decodifica cabeceras MIME."""
        if not value:
            return ""
        parts = decode_header(value)
        decoded = []
        for part, charset in parts:
            if isinstance(part, bytes):
                decoded.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                decoded.append(part)
        return " ".join(decoded)
