import json
import logging
import hmac
import hashlib
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class GitHubController(http.Controller):

    def _verify_signature(self, req):
        """Verifica que la petición viene de GitHub y no es una falsificación."""
        signature = req.httprequest.headers.get("X-Hub-Signature-256")
        
        secret = request.env["ir.config_parameter"].sudo().get_param("github.webhook_secret")
        if not secret:
            _logger.error("El secreto del webhook de GitHub no está configurado en los Parámetros del Sistema.")
            return False

        if not signature:
            _logger.warning("Petición a webhook de GitHub sin firma.")
            return False

        sha_name, signature_hex = signature.split("=", 1)
        if sha_name != "sha256":
            return False

        mac = hmac.new(
            secret.encode("utf-8"), msg=req.httprequest.data, digestmod=hashlib.sha256
        )
        return hmac.compare_digest(mac.hexdigest(), signature_hex)

    def _post_message_to_channel(self, message_body):
        """Publica un mensaje formateado en el canal de Discuss."""
        try:
            channel_id_str = request.env["ir.config_parameter"].sudo().get_param("github.target_channel_id")
            if not channel_id_str:
                _logger.error("El ID del canal de destino no está configurado en los Parámetros del Sistema.")
                return

            channel_id = int(channel_id_str)
            channel = request.env["mail.channel"].browse(channel_id).sudo()
            if channel.exists():
                channel.message_post(
                    body=message_body,
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                )
                _logger.info(f"Mensaje publicado en el canal ID {channel_id}")
            else:
                _logger.error(
                    f"No se encontró el canal de Discuss con ID {channel_id}"
                )
        except Exception as e:
            _logger.error(f"Error al intentar publicar en el canal de Discuss: {e}")

    @http.route(
        "/github/webhook", type="json", auth="public", methods=["POST"], csrf=False
    )
    def github_webhook_handler(self, **kwargs):
        """Punto de entrada principal para el webhook de GitHub."""

        if not self._verify_signature(request):
            _logger.warning("Firma de webhook de GitHub inválida. Petición descartada.")
            return "Forbidden", 403

        event = request.httprequest.headers.get("X-GitHub-Event")
        payload = json.loads(request.httprequest.data)
        _logger.info(f"Webhook de GitHub recibido: Evento '{event}'")

        message = ""
        if event == "pull_request":
            action = payload.get("action")
            pr = payload.get("pull_request", {})
            user = pr.get("user", {}).get("login")
            title = pr.get("title")
            url = pr.get("html_url")

            if action == "opened":
                message = f"🚀 **Nuevo Pull Request** abierto por *{user}*\n**[{title}]({url})**"
            elif action == "closed":
                if pr.get("merged"):
                    message = f"✅ **Pull Request Merged!**\n**[{title}]({url})** ha sido mergeado."
                else:
                    message = f"❌ **Pull Request Cerrado** sin mergear.\n**[{title}]({url})**"

        elif event == "issue_comment" and payload.get("action") == "created":
            comment = payload.get("comment", {})
            user = comment.get("user", {}).get("login")
            body = comment.get("body")
            url = comment.get("html_url")
            issue_title = payload.get("issue", {}).get("title")

            message = f"💬 **Nuevo Comentario** de *{user}* en **[{issue_title}]({url})**:\n> {body}"

        if message:
            self._post_message_to_channel(message)

        return "OK"
