#!/usr/bin/python3
# -*-coding:utf-8 -*-

import os

import redis


""" Redis Connection 모듈
RDConnector(데이터베이스 처리)

- Redis ConnectionPool 사용
"""


class RDConnector:
    def __init__(self):
        """Redis Connector"""
        self._connection = None
        self.create_pool()

    @property
    def connection(self):
        """Property Connection"""
        return self._connection

    def create_pool(self):
        """Make Connection Pool"""

        pool = redis.ConnectionPool(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT", 6379),
            db=os.getenv("REDIS_DB", 0),
            password=os.getenv("REDIS_PASSWORD"),
            socket_timeout=int(os.getenv("REDIS_TIMEOUT", 5)),
        )

        self._connection = redis.Redis(connection_pool=pool)


if __name__ == "__main__":
    rdc = RDConnector()