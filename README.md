## 프로젝트 구조

```text
.
├─ sql
│  └─ edu_shopping_setup.sql
├─ main.py
├─ .gitignore
└─ README.md
```

| 파일/폴더 | 설명 |
|---|---|
| `sql/edu_shopping_setup.sql` | Supabase SQL Editor에서 실행할 전체 SQL 파일 |
| `main.py` | Python 실행 파일 |
| `.gitignore` | GitHub에 올리면 안 되는 파일 제외 설정 |
| `README.md` | 프로젝트 실행 설명서 |

---

## 주요 기능

프로그램 실행 후 아래 메뉴를 사용할 수 있습니다.

```text
1. 상품 목록 보기
2. 상품 주문하기
3. 현재 세션 주문 내역 보기
4. DB 최근 주문 내역 보기
5. 종료
```

| 메뉴 | 설명 |
|---|---|
| `1. 상품 목록 보기` | 판매 중인 상품과 재고를 조회합니다. |
| `2. 상품 주문하기` | 신규 고객 등록, 주문 생성, 주문상세 생성, 재고 차감을 수행합니다. |
| `3. 현재 세션 주문 내역 보기` | 현재 프로그램 실행 중 생성한 주문 내역을 확인합니다. |
| `4. DB 최근 주문 내역 보기` | Supabase DB에 저장된 최근 주문 내역을 조회합니다. |

---

## 사용 기술

- Python 3.12
- Supabase
- PostgreSQL
- PL/pgSQL
- python-dotenv
- supabase-py

---

## 실행 순서 요약

처음 이 프로젝트를 받은 사람은 아래 순서대로 진행하면 됩니다.

```text
1. 저장소 clone 또는 브랜치 pull
2. Supabase에서 SQL 파일 실행
3. Supabase Data API 설정 확인
4. Python 가상환경 생성
5. 가상환경 활성화
6. 필요한 라이브러리 설치
7. .env 파일 생성
8. python main.py 실행
```

---

## 1. 저장소 clone 또는 브랜치 가져오기

저장소를 처음 받는 경우:

```bash
git clone https://github.com/rkdthjwd-jpg/s-2team.git
cd s-2team
```

특정 브랜치를 받아야 하는 경우:

```bash
git fetch origin
git checkout -b feature/edu-shopping-python-chisoo origin/feature/edu-shopping-python-chisoo
```

이미 저장소가 있는 경우:

```bash
git fetch origin
git checkout feature/edu-shopping-python-chisoo
git pull origin feature/edu-shopping-python-chisoo
```

현재 브랜치 확인:

```bash
git branch
```

아래처럼 현재 브랜치 앞에 `*`가 붙어 있으면 됩니다.

```text
* feature/edu-shopping-python-chisoo
```

---

## 2. Supabase SQL 실행

Supabase Dashboard에서 SQL Editor로 이동합니다.

```text
Supabase Dashboard
→ 프로젝트 선택
→ SQL Editor
→ New query
```

아래 파일 내용을 복사해서 실행합니다.

```text
sql/edu_shopping_setup.sql
```

이 SQL 파일은 아래 작업을 수행합니다.

```text
1. edu_shopping 스키마 생성
2. customers 테이블 생성
3. product_categories 테이블 생성
4. products 테이블 생성
5. orders 테이블 생성
6. order_items 테이블 생성
7. inventory 테이블 생성
8. 샘플 데이터 삽입
9. 상품 조회용 View 생성
10. 주문 처리용 RPC 함수 생성
11. Supabase API 권한 설정
```

주의사항:

```sql
DROP SCHEMA IF EXISTS edu_shopping CASCADE;
```

SQL 파일에 위 코드가 포함되어 있으므로, 다시 실행하면 기존 `edu_shopping` 스키마와 데이터가 모두 삭제되고 초기화됩니다.

처음 세팅할 때만 전체 실행하는 것을 권장합니다.

---

## 3. Supabase Data API 설정 확인

Python 코드에서 Supabase API를 통해 DB에 접근하려면 스키마가 Data API에 노출되어 있어야 합니다.

Supabase Dashboard에서 아래 메뉴로 이동합니다.

```text
Settings
→ Data API
→ Exposed schemas
```

아래 스키마가 포함되어 있는지 확인합니다.

```text
public
edu_shopping
```

`public`은 기본으로 포함되어 있는 경우가 많고, `edu_shopping`은 직접 추가해야 할 수 있습니다.

---

## 4. Python 3.12 설치 확인

이 프로젝트는 Python 3.12 사용을 권장합니다.

설치된 Python 버전 확인:

```powershell
py -0
```

예시:

```text
-V:3.12
```

Python 3.12가 없다면 Python 3.12.x Windows 64-bit 버전을 설치합니다.

---

## 5. Python 가상환경 생성

프로젝트 폴더에서 아래 명령어를 실행합니다.

Windows PowerShell 기준:

```powershell
py -3.12 -m venv .venv
```

이 명령어는 현재 프로젝트 폴더 안에 `.venv`라는 가상환경을 생성합니다.

가상환경은 이 프로젝트에서 사용할 Python과 라이브러리를 따로 관리하는 공간입니다.

---

## 6. 가상환경 활성화

Windows PowerShell 기준:

```powershell
.venv\Scripts\Activate.ps1
```

만약 아래와 같은 오류가 발생하면:

```text
이 시스템에서 스크립트를 실행할 수 없으므로 ...
```

아래 명령어를 먼저 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

그다음 다시 활성화합니다.

```powershell
.venv\Scripts\Activate.ps1
```

성공하면 터미널 앞에 `(.venv)`가 붙습니다.

```powershell
(.venv) PS C:\경로>
```

---

## 7. 필요한 라이브러리 설치

가상환경이 활성화된 상태에서 아래 명령어를 실행합니다.

```powershell
pip install supabase python-dotenv
```

이 프로젝트에서 사용하는 외부 라이브러리는 아래와 같습니다.

| 라이브러리 | 용도 |
|---|---|
| `supabase` | Python에서 Supabase API를 호출하기 위해 사용 |
| `python-dotenv` | `.env` 파일의 환경변수를 읽기 위해 사용 |

설치가 끝나면 아래 import가 정상 동작해야 합니다.

```python
from dotenv import load_dotenv
from supabase import create_client
```

---

## 8. `.env` 파일 생성

프로젝트 루트에 `.env` 파일을 직접 생성합니다.

```text
.
├─ main.py
├─ .env
└─ sql
```

`.env` 파일 내용:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-public-key
```

### SUPABASE_URL 가져오는 위치

```text
Supabase Dashboard
→ Settings
→ Data API
→ Project URL 또는 API URL
```

만약 화면에 아래처럼 `/rest/v1`까지 붙어 있다면:

```text
https://xxxxxxxxxxxxxxxxxxxx.supabase.co/rest/v1
```

`.env`에는 `/rest/v1`을 빼고 입력합니다.

```env
SUPABASE_URL=https://xxxxxxxxxxxxxxxxxxxx.supabase.co
```

### SUPABASE_ANON_KEY 가져오는 위치

```text
Supabase Dashboard
→ Settings
→ API Keys
→ anon public key
```

주의사항:

```text
anon public key는 사용 가능
service_role key는 사용하지 말 것
```

`service_role` 키는 관리자 권한이므로 로컬 실습 코드나 GitHub에 절대 넣으면 안 됩니다.

---

## 9. 프로그램 실행

가상환경이 활성화된 상태에서 아래 명령어를 실행합니다.

```powershell
python main.py
```

정상 실행되면 아래 메뉴가 표시됩니다.

```text
=== 미니 이커머스 시스템 ===
1. 상품 목록 보기
2. 상품 주문하기
3. 현재 세션 주문 내역 보기
4. DB 최근 주문 내역 보기
5. 종료
```

---

## 10. 처음 테스트하는 방법

처음 실행할 때는 아래 순서로 테스트하는 것을 권장합니다.

### 1단계: 상품 목록 조회

메뉴에서 `1` 입력

```text
1. 상품 목록 보기
```

상품 목록이 나오면 Python과 Supabase 연결이 정상입니다.

### 2단계: 상품 주문하기

메뉴에서 `2` 입력

```text
2. 상품 주문하기
```

입력 예시:

```text
사용할 고객 ID: 11
고객 이름: 홍길동
전화번호: 010-1111-2222
이메일: 엔터 또는 test@example.com
구매할 상품 ID: 102
구매할 수량: 1
결제수단: CARD
```

기존 샘플 고객 ID는 `1~10`까지 이미 사용 중입니다.  
따라서 새 주문 테스트 시에는 `11`, `12`, `13`처럼 아직 없는 고객 ID를 입력해야 합니다.

상품 ID는 상품 목록의 가장 왼쪽 숫자입니다.

예시:

| 상품 ID | 상품명 |
|---:|---|
| 101 | 베이직 코튼 티셔츠 |
| 102 | 오버핏 린넨 셔츠 |
| 103 | 스웨트 맨투맨 |
| 104 | 후드 집업 |
| 105 | 데님 팬츠 |
| 106 | 와이드 슬랙스 |
| 107 | 치노 팬츠 |
| 108 | 트렌치 코트 |
| 109 | 울 가디건 |
| 110 | 니트 원피스 |

---

## 11. Supabase에서 주문 결과 확인

주문이 성공하면 Supabase SQL Editor에서 아래 쿼리로 결과를 확인할 수 있습니다.

### 고객 확인

```sql
SELECT *
FROM edu_shopping.customers
ORDER BY customer_id DESC;
```

### 주문 확인

```sql
SELECT *
FROM edu_shopping.orders
ORDER BY order_id DESC;
```

### 주문상세 확인

```sql
SELECT *
FROM edu_shopping.order_items
ORDER BY order_item_id DESC;
```

### 재고 확인

```sql
SELECT *
FROM edu_shopping.inventory
ORDER BY product_id;
```

---

## 12. 가상환경이 필요한 이유

이 프로젝트는 Python 기본 기능만 사용하는 것이 아니라 외부 라이브러리를 사용합니다.

```python
from supabase import create_client
from dotenv import load_dotenv
```

따라서 각자 PC에 필요한 라이브러리를 설치해야 합니다.

가상환경은 프로젝트 전용 Python 실행 공간입니다.

```text
프로젝트 폴더
├─ .venv
│  └─ 이 프로젝트 전용 라이브러리
├─ main.py
└─ sql
```

가상환경을 쓰면 다른 Python 프로젝트와 라이브러리 버전이 섞이지 않습니다.

`.venv` 폴더는 GitHub에 올리지 않습니다.  
각자 로컬에서 직접 생성해야 합니다.

---

## 13. GitHub에 올리면 안 되는 파일

아래 파일은 GitHub에 올리면 안 됩니다.

```text
.env
.venv/
__pycache__/
```

현재 `.gitignore`에는 아래 내용이 포함되어 있어야 합니다.

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd

# Virtual environment
.venv/
venv/
env/

# Environment variables
.env
.env.*

# VS Code
.vscode/

# OS
.DS_Store
Thumbs.db
```

---

## 14. 자주 발생하는 오류

### 1. `ModuleNotFoundError: No module named 'supabase'`

원인: `supabase` 라이브러리가 설치되지 않았습니다.

해결:

```powershell
pip install supabase
```

또는:

```powershell
pip install supabase python-dotenv
```

---

### 2. `ModuleNotFoundError: No module named 'dotenv'`

원인: `python-dotenv` 라이브러리가 설치되지 않았습니다.

해결:

```powershell
pip install python-dotenv
```

---

### 3. `.env`를 못 읽는 경우

확인할 것:

```text
1. .env 파일이 main.py와 같은 위치에 있는지
2. 파일명이 .env.txt가 아닌지
3. SUPABASE_URL 오타가 없는지
4. SUPABASE_ANON_KEY 오타가 없는지
```

---

### 4. 상품 목록 조회 실패

확인할 것:

```text
1. Supabase SQL Editor에서 sql/edu_shopping_setup.sql을 실행했는지
2. public.v_edu_shopping_active_products View가 생성되었는지
3. Supabase Data API에서 public 스키마가 노출되어 있는지
4. 권한 GRANT가 실행되었는지
```

확인 쿼리:

```sql
SELECT *
FROM public.v_edu_shopping_active_products;
```

---

### 5. 주문 처리 실패

확인할 것:

```text
1. 고객 ID가 이미 존재하지 않는지
2. 전화번호가 이미 등록되어 있지 않은지
3. 이메일을 입력했다면 이미 등록된 이메일이 아닌지
4. 상품 ID가 존재하는지
5. 구매 수량이 재고보다 많지 않은지
6. place_edu_shopping_order 함수가 생성되어 있는지
```

함수 확인 쿼리:

```sql
SELECT
    routine_schema,
    routine_name
FROM information_schema.routines
WHERE routine_name = 'place_edu_shopping_order';
```

---

## 15. 전체 실행 명령어 요약

Windows PowerShell 기준:

```powershell
git fetch origin
git checkout feature/edu-shopping-python-chisoo
git pull origin feature/edu-shopping-python-chisoo

py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1

pip install supabase python-dotenv

python main.py
```

---

## 16. 개발자가 수정 후 GitHub에 반영하는 방법

파일 수정 후 상태 확인:

```powershell
git status
```

변경 파일 추가:

```powershell
git add .
```

커밋:

```powershell
git commit -m "docs: update README setup guide"
```

푸시:

```powershell
git push
```
