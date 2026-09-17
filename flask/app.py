#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

from flask import Flask, request
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from v2.handlers.receiver.receiver import MailReceiveHandler


"""
Push Server

Flask API를 통해 알림 데이터를 수신하고
Receiver를 통해 Redis Queue에 전달한다.
"""


app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
)

CORS(app)

logger = logging.getLogger(__name__)

_receiver = MailReceiveHandler()


@app.route("/notify", methods=["POST"])
def notify():
    """메일 Push 알림 수신"""

    try:
        data = request.get_json(silent=True)

        if not data:
            return {"result": "invalid payload"}, 400

        forwarded_for = request.headers.get("X-Forwarded-For")

        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.remote_addr or ""

        result = _receiver.receive_notification(
            data=data,
            ip=client_ip,
        )

        if not result:
            return {"result": "ignored"}, 200

        return {"result": "success"}, 200

    except Exception as e:
        logger.exception("Notification receive failed: %s", e)

        return {"result": "error"}, 500


@app.route("/health", methods=["GET"])
def health():
    """서버 상태 확인"""

    return {
        "status": "ok",
        "service": "push-server",
    }, 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
    )