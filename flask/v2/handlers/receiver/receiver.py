#!/usr/bin/python3
# -*- coding: utf-8 -*-

from v2.models.notification import MailModel


""" 메일 알림 수신

이메일 알림 데이터를 수신하여
Redis Push Queue에 적재한다.
"""


_mail_model = MailModel()


class MailReceiveHandler:

    def receive_notification(self, data, ip):
        """이메일 알림 수신"""

        if not data:
            return False

        # 발송 제외 타입
        if data.get("type") in ("organ1", "user1"):
            return False

        email = data.get("to", "")

        if not email:
            return False

        data["ip"] = ip

        return _mail_model.put_noti(data)


if __name__ == "__main__":
    receiver = MailReceiveHandler()