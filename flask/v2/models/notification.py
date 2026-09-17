#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from v2.databases.redis import RDConnector


""" 메일 알림 저장
이메일 수신시 '보낸사람, 제목'으로 구성된 알림데이터 수신하면
Redis에 큐로 적재한다.
"""

_rd = RDConnector()

#: 큐이름
NOTI_QUEUE_MAIL = "notification:mail"


class MailModel:
    def __init__(self):
        pass

    def put_noti(self, data):
        """메일발송데이터 저장"""
        conn = _rd.connection

        if not conn or not data:
            return False

        an_email = data.get("to", "")

        if not an_email:
            return False

        try:
            n_data = {
                "type": data.get("type", ""),
                "from": data.get("from", ""),
                "to": data.get("to", ""),
                "kind": data.get("kind", ""),
                "subject": data.get("subject", ""),
                "content": data.get("content", ""),
            }

            conn.rpush(
                NOTI_QUEUE_MAIL,
                json.dumps(n_data, ensure_ascii=False),
            )

            return True

        except Exception:
            return False


if __name__ == "__main__":
    mm = MailModel()