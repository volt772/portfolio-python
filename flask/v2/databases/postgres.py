#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

from psycopg2 import pool
from psycopg2.extras import RealDictCursor


"""
PostgreSQL Connection 모듈

- ThreadedConnectionPool 사용
- 사용자 / Push Token 데이터 조회 및 관리
"""


class PGConnector:

    def __init__(self):
        self.connection_pool = None
        self.create_pool()

    def create_pool(self):
        """PostgreSQL Connection Pool 생성"""

        self.connection_pool = pool.ThreadedConnectionPool(
            minconn=int(os.getenv("DB_MIN_CONNECTION", 1)),
            maxconn=int(os.getenv("DB_MAX_CONNECTION", 10)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432),
            database=os.getenv("DB_NAME"),
        )

    def get_conn(self):
        """Connection 요청"""

        return self.connection_pool.getconn()

    def put_conn(self, connection):
        """Connection 반환"""

        if connection:
            self.connection_pool.putconn(connection)

    def destroy(self):
        """Connection Pool 종료"""

        if self.connection_pool:
            self.connection_pool.closeall()

    def fetch_one(self, query, params=None):
        """단일 데이터 조회"""

        connection = self.get_conn()

        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                row = cursor.fetchone()

                return dict(row) if row else None

        finally:
            self.put_conn(connection)

    def fetch_all(self, query, params=None):
        """다중 데이터 조회"""

        connection = self.get_conn()

        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                rows = cursor.fetchall()

                return [dict(row) for row in rows]

        finally:
            self.put_conn(connection)

    def execute(self, query, params=None):
        """INSERT / UPDATE / DELETE 실행"""

        connection = self.get_conn()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                connection.commit()

                return cursor.rowcount

        except Exception:
            connection.rollback()
            raise

        finally:
            self.put_conn(connection)