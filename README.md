# Python Portfolio

Python 기반 백엔드 개발 경험을 정리한 포트폴리오 저장소입니다.

FastAPI를 활용한 날씨 API 서버와 Flask 기반 Push 서버 예제 코드로 구성되어 있습니다.

---

## 1. FastAPI Weather API

야구장 위치를 기준으로 현재 날씨와 예보 데이터를 제공하는 REST API 서버입니다.

### 주요 기능

- FastAPI 기반 REST API 구현
- 외부 날씨 API 연동
- 현재 날씨 / 예보 데이터 비동기 조회
- PostgreSQL 기반 날씨 데이터 저장 및 조회
- 동일 시간대 중복 API 호출 방지를 위한 데이터 확인
- Connection Pool 기반 DB 연결 관리

### 주요 기술

- Python
- FastAPI
- PostgreSQL
- HTTPX
- asyncio
- REST API

### 프로젝트 구조

```text
fastAPI/
├── api/
│   └── weather_request.py
├── base/
│   └── weather_schema.py
├── controllers/
│   └── weather.py
├── database/
│   └── database_connection.py
├── models/
│   └── weather.py
├── utils/
│   └── helpers.py
└── main.py
```

---

## 2. Flask Push Server

모바일 애플리케이션에 Push 알림을 전달하기 위한 서버 구조입니다.

Flask API를 통해 알림 요청을 수신하고 Redis Queue에 저장한 뒤,
Worker가 Queue 데이터를 조회하여 발송 대상 기기 정보를 확인하고 Push 발송 데이터를 구성합니다.

### 주요 기능

- Flask 기반 Push 요청 API 구현
- Redis Queue 기반 비동기 알림 처리
- PostgreSQL 기반 사용자 및 Push Token 정보 관리
- Redis 기반 사용자 기기정보 캐시
- Worker 프로세스를 통한 Queue 처리
- FCM Push 발송 데이터 구성
- PostgreSQL / Redis Connection Pool 사용

### 처리 흐름

```text
Client
  ↓
Flask API
  ↓
Receiver
  ↓
Redis Queue
  ↓
Queue Worker
  ↓
Sender
  ↓
FCM Push
```

### 주요 기술

- Python
- Flask
- PostgreSQL
- Redis
- Multiprocessing
- REST API
- FCM

### 프로젝트 구조

```text
flask/
├── app.py
└── v2/
    ├── databases/
    │   ├── postgres.py
    │   └── redis.py
    ├── handlers/
    │   ├── receiver/
    │   │   └── receiver.py
    │   └── sender/
    │       ├── queue_service.py
    │       └── sender.py
    ├── models/
    │   ├── notification.py
    │   └── user.py
    └── workers/
        └── queue_worker.py
```

---

## Note

포트폴리오 공개를 위해 실제 운영 환경의 인증정보, 서버정보 및 일부 업무 로직은 제외하거나 단순화했습니다.

API Key, DB 접속정보, Redis 접속정보 등은 환경변수를 통해 관리하도록 구성했습니다.
