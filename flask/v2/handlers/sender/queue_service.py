#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os

from v2.databases.redis import RDConnector


""" 큐 처리기
Redis에 저장된 알림 큐를 가져온다.
"""


_rd = RDConnector()

NOTI_QUEUE_MAIL = "notification:mail"
NOTI_QUEUE_EXTRAS = "notification:extras"
NOTI_QUEUE_PROMPT = "notification:prompt"


class SenderQueue:

    def __init__(self):
        #: 큐 Bulk Select 사이즈
        self.pop_size = int(os.getenv("QUEUE_POP_SIZE", 100))

    def put_exception_data(self, data):
        """실패데이터 다시 밀어넣기"""

        if not data:
            return False

        conn = _rd.connection

        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)

        conn.rpush(NOTI_QUEUE_MAIL, data)

        return True

    def multi_pop(self, redis_conn, queue_name, size):
        """다중 pop"""

        pipeline = redis_conn.pipeline()

        pipeline.lrange(queue_name, 0, size - 1)
        pipeline.ltrim(queue_name, size, -1)

        return pipeline.execute()

    def get_notidata(self, q_type="mail"):
        """알림 발송 데이터 가져오기"""

        conn = _rd.connection

        if not conn:
            return []

        if q_type == "mail":
            queue_name = NOTI_QUEUE_MAIL
            pop_size = self.pop_size

        elif q_type == "prompts":
            queue_name = NOTI_QUEUE_PROMPT
            pop_size = max(int(self.pop_size / 2), 1)

        else:
            queue_name = NOTI_QUEUE_EXTRAS
            pop_size = max(int(self.pop_size / 2), 1)

        result = self.multi_pop(
            conn,
            queue_name,
            pop_size,
        )

        noti_data = []

        if not result:
            return noti_data

        queues = result[0]

        for data in queues:
            try:
                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                noti_data.append(
                    self.arrange_notidata(data)
                )

            except Exception:
                continue

        return noti_data

    def arrange_notidata(self, data):
        """알림 데이터 정리"""

        if not data:
            return {}

        if isinstance(data, dict):
            return data

        return json.loads(data)


if __name__ == "__main__":
    queue = SenderQueue()