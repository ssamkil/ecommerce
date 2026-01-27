***
## e-commerce 사이트 주요 REST API 기능 구현
***
> ### ERD
![Cap 2023-11-09 09-37-54-595](https://github.com/ssamkil/ecommerce/assets/10840728/76641d78-ea34-4f9c-a473-976bbfaeff6d)
***
> ### 기능 구현
  1. 유저
    - 회원가입 (가입시 비밀번호 암호화 후 데이터베이스에 저장)
    - 로그인 (jwt 기반 인가 구현, allauth 사용한 카카오 소셜 로그인 구현 -> db 에 회원 정보 없을 시 자동 회원가입)
      
  2. 게시글
    - GET, POST, PATCH, DELETE
      
  3. 판매 상품
    - GET, POST, PATCH, DELETE
      
  4. 장바구니
    - GET, POST (장바구니에 상품이 이미 존재할 시 재고 수량 PATCH), DELETE
      
  5. 리뷰
    - 판매 상 항목과 1:M 관계
      
  6. 주문
    - 주문시 장바구니 상품들을 주문 db로 옮긴 후 장바구니 초기화
***
> ### 기술 스택
  * Python, Django, MySQL, jwt, Docker, Git, Trello
> ### 그 외
  * 테스트코드 작성으로 기능 별 오류 유무 재차 확인
