#!/usr/bin/python3
# -*- coding: utf-8 -*-

import ast
import os

from v2.databases.postgres import PGConnector
from v2.databases.redis import RDConnector


""" 사용자 정보 처리

PostgreSQL
- 사용자 / 기기 / Push Token 정보 관리

Redis
- Push 발송에 필요한 기기정보 캐시 관리
"""


_pg = PGConnector()
_rd = RDConnector()

USER_KEY = os.getenv("REDIS_USER_KEY", "notification:user:")


class UserModel:

    def get_users(self, email):
        """이메일 기준 기기정보 조회"""

        return _pg.fetch_all(
            """
            SELECT *
            FROM noti_user
            WHERE nu_email = %s
            """,
            (email,),
        )

    def get_user_by_uuid(self, email, uuid):
        """이메일, UUID 기준 기기정보 조회"""

        user = _pg.fetch_one(
            """
            SELECT nu_data
            FROM noti_user
            WHERE nu_email = %s
              AND nu_uuid = %s
            """,
            (email, uuid),
        )

        if user:
            return user["nu_data"]

        return None

    def delete_users(self, data, is_all=False):
        """사용자 정보 삭제"""

        if not data:
            return False

        email = data.get("an_email", "")
        uuid = data.get("an_uuid", "")

        if not email:
            return False

        try:

            if is_all:
                _pg.execute(
                    """
                    DELETE FROM noti_user
                    WHERE nu_email = %s
                      AND nu_type != 'WEBHOOK'
                    """,
                    (email,),
                )

            elif uuid:
                _pg.execute(
                    """
                    DELETE FROM noti_user
                    WHERE nu_email = %s
                      AND nu_uuid = %s
                    """,
                    (email, uuid),
                )

            users = self.get_users(email)

            self.update_user_cache(
                email=email,
                users=users,
            )

            return users

        except Exception:
            return False

    def get_device_info(self, email):
        """Redis 사용자 기기정보 조회"""

        if not email:
            return False

        conn = _rd.connection

        if not conn:
            return False

        try:
            device_info = conn.hget(
                USER_KEY + email,
                "deviceInfo",
            )

            if not device_info:
                return {}

            if isinstance(device_info, bytes):
                device_info = device_info.decode("utf-8")

            return ast.literal_eval(device_info)

        except Exception:
            return {}

    def update_user_cache(self, email, users):
        """PostgreSQL 데이터를 기준으로 Redis 캐시 갱신"""

        if not email:
            return False

        conn = _rd.connection

        if not conn:
            return False

        conn.delete(USER_KEY + email)

        if not users:
            return True

        return self._insert_redis_data(
            email=email,
            users=users,
        )

    def delete_user_cache(self, email):
        """Redis 사용자 캐시 삭제"""

        if not email:
            return False

        conn = _rd.connection

        if not conn:
            return False

        conn.delete(USER_KEY + email)

        return True

    def _insert_redis_data(self, email, users):
        """사용자 기기정보 Redis 저장"""

        conn = _rd.connection

        if not conn or not users:
            return False

        device_info = {}

        try:

            for user in users:

                uuid = user["nu_uuid"]
                settings = user.get("nu_data") or {}

                device_info[uuid] = {
                    "an_type": user["nu_type"],
                    "an_email": user["nu_email"],
                    "an_token": user["nu_token"],
                    "an_uuid": uuid,
                }

                if uuid.endswith("vh_task"):

                    device_info[uuid]["au_host"] = settings.get("host", "")

                else:

                    device_info[uuid]["au_mail"] = settings.get("au_mail", [])
                    device_info[uuid]["au_eas"] = settings.get("au_eas", [])
                    device_info[uuid]["au_cal"] = settings.get("au_cal", [])
                    device_info[uuid]["au_time"] = settings.get("au_time", [])
                    device_info[uuid]["au_all"] = settings.get("au_all", {})

                    if "au_board" in settings:
                        device_info[uuid]["au_board"] = settings["au_board"]

                    if "nu_hook_curl" in user:
                        device_info[uuid]["au_hook_curl"] = user["nu_hook_curl"]

            conn.hset(
                USER_KEY + email,
                mapping={
                    "deviceInfo": str(device_info),
                },
            )

            return True

        except Exception:
            return False


if __name__ == "__main__":
    user_model = UserModel()