***
## e-commerce 사이트 주요 REST API 기능 구현
***
> ### ERD
<img width="1323" height="1218" alt="Untitled" src="https://github.com/user-attachments/assets/3ed9d188-73af-40c2-82ef-b934471e4c50" />

***
> ### 시스템 아키텍처
<img width="1040" height="662" alt="diagram-export-2026 -3 -12 -오후-3_22_29" src="https://github.com/user-attachments/assets/409c9baa-a5da-432b-a348-4a622755cd6b" />

***
> ### 기술 스택
  * Python, Django, PostgreSQL, Redis, Celery, Sentry, Docker, Nginx, AWS EC2, Github Actions, Locust, Git

***
> ### 기능 구현
1. 주문 자동화 및 비동기 재고 관리
  - Celery Beat 기반 주문 만료 처리: 미결제 주문을 5분 단위로 체크하여 자동 취소하고 재고를 복구하는 스케줄러를 구현했습니다.
  - 비동기 작업 분리: 응답 시간이 긴 로직을 Redis와 Celery를 통해 비동기로 처리하여 사용자 경험을 개선했습니다.

2. 2-Depth 계층형 댓글 및 커뮤니티 시스템
  - Self-Referencing 구조: parent 외래 키를 활용해 댓글-대댓글 간의 부모-자식 관계를 설계했습니다.
  - Depth 제어 로직: Serializer 레벨에서 계층 깊이를 2단계로 제한하여 뎁스 심화를 방지하고 쿼리 효율성을 높였습니다.

3. 보안
  - Bcrypt 암호화: 사용자 비밀번호를 Bcrypt를 사용하여 단방향 해싱함으로써 보안성을 강화했습니다.

4. 가시성 확보 및 성능 최적화
  - 실시간 에러 모니터링: Sentry를 연동하여 분산 환경에서 발생하는 예외 상황을 실시간으로 추적하고 대응할 수 있는 환경을 구축했습니다.
  - 부하 테스트(Locust): 핵심 엔드포인트에 대한 부하 테스트를 수행하여 시스템 임계치를 점검하고 병목 현상을 분석했습니다.
    
***
> ### 테스트 커버리지
  * Test Summary
    - 프로젝트의 안정성과 데이터 무결성을 보장하기 위해 핵심 비즈니스 로직에 대해 82% 이상의 유닛 테스트 커버리지를 달성하였습니다.

> API Documentation
  - http://3.107.250.88:80/api/schema/swagger-ui/
