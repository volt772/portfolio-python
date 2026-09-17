#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import time
from multiprocessing import Process, cpu_count

from v2.handlers.sender.sender import SendDispatcher


""" 큐 실행기
Redis에 저장된 알림큐를 순차적으로 꺼낸 후,
발송할 수 있도록 발송기에 전달
"""


logger = logging.getLogger(__name__)

_dispatcher = SendDispatcher()


def run():
    while True:
        try:
            _dispatcher.send_notification()
            time.sleep(1.0)

        except Exception as e:
            logger.exception("Queue worker error: %s", e)
            time.sleep(1.0)


if __name__ == "__main__":

    #: CPU Core 기준 Worker 생성
    num_cores = max(cpu_count() - 2, 1)

    processes = []

    for _ in range(num_cores):
        processes.append(
            Process(
                target=run,
                args=(),
            )
        )

    for process in processes:
        process.start()

    for process in processes:
        process.join()