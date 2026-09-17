#!/usr/bin/python3
# -*- coding: utf-8 -*-

from v2.handlers.sender.queue_service import SenderQueue
from v2.models.user import UserModel


""" 알림 발송기
큐에서 알림을 뺀 후 발송 대상 기기를 조회하고 Push 발송 데이터를 구성한다.

1단계 : Redis Queue에서 알림 데이터를 가져온다.
2단계 : 사용자 기기정보를 Redis에서 조회한다.
3단계 : 발송 대상 데이터를 구성한다.
4단계 : FCM Push를 발송한다.
"""


_queue = SenderQueue()
_user_model = UserModel()


class SendDispatcher:
    def __init__(self):
        pass

    def send_notification(self):
        """메일알림발송"""

        mail_queues = _queue.get_notidata("mail")

        for mail_queue in mail_queues:

            if not mail_queue:
                continue

            fcm_bundle = self.make_fcm_bundle(
                mail_queue,
                "mail",
            )

            if not fcm_bundle:
                continue

            self.send_fcm(fcm_bundle)

    def send_calendar(self, calendar_list):
        """캘린더알림발송"""

        for calendar in calendar_list:
            if not calendar:
                continue

            # 캘린더 Push 발송 처리
            # ... 중략 ...

    def make_fcm_bundle(self, queue_data, send_type="mail"):
        """기기정보 조회 및 FCM 발송 데이터 구성"""

        email = queue_data.get("to", "")

        if not email:
            return {}

        #: 사용자 기기정보 조회
        devices = _user_model.get_device_info(email)

        if not devices:
            return {}

        if send_type == "mail":

            # 사용자 알림 설정에 따른 기기 선별
            # ... 중략 ...

            pass

        fcm_bundle = {
            "devices": devices,
            "email": email,
            "queue_data": queue_data,
            "send_type": send_type,
        }

        return fcm_bundle

    def send_fcm(self, fcm_bundle):
        """FCM Push 발송"""

        devices = fcm_bundle["devices"]
        queue_data = fcm_bundle["queue_data"]

        for uuid, device in devices.items():

            token = device.get("an_token")

            if not token:
                continue

            # FCM Push 발송
            # token, title, body 등을 구성하여 Firebase에 전달
            # ... 중략 ...

    def get_device_only_mobile(self, devices):
        """모바일 기기만 선별"""

        if not devices:
            return {}

        result = {}

        for uuid, device in devices.items():

            device_type = device.get("an_type", "")

            if device_type in ("ANDROID", "IOS"):
                result[uuid] = device

        return result


if __name__ == "__main__":
    dispatcher = SendDispatcher()
    dispatcher.send_notification()