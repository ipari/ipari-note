# ipari-note

Obsidian으로 관리하는 Markdown 문서를 웹에서 열람하고 편집할 수 있는 개인용 노트 겸 블로그입니다.

문서 변경을 감지해 HTML로 렌더링하고 데이터베이스에 반영하며, 문서별 공개 범위를 설정할 수 있습니다.

## 주요 기능

- 원하는 Markdown 편집기와 함께 사용
- Markdown 문서 변경 감지 및 자동 렌더링
- 웹에서 문서 열람·작성·편집
- 공개, 링크 공개, 비공개 권한 설정
- 게시물 목록과 상단 고정
- 태그와 중첩 태그 경로 지원
- Obsidian 위키 링크 및 이미지 임베드 지원
- 작업 체크박스 렌더링 및 웹에서 상태 변경
- 클립보드를 통한 이미지 업로드
- 웹 설정 화면 제공
- RSS, Atom, 사이트맵 생성

## 설치

저장소를 받은 뒤 Python 가상환경을 만들고 의존성을 설치합니다.

```shell
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS 또는 Linux:

```shell
source .venv/bin/activate
pip install -r requirements.txt
```

Gunicorn으로 실행하려면 Gunicorn도 설치합니다.

```shell
pip install gunicorn
```

## 설정

예제 설정 파일에서 `.bak` 확장자를 제거한 파일을 만듭니다.

```text
config.py.bak  → config.py
config.yml.bak → config.yml
user.yml.bak   → user.yml
```

각 파일의 역할은 다음과 같습니다.

- `config.py`: Flask, SQLAlchemy, URL prefix, 파일 감시 방식
- `config.yml`: 노트 제목, 테마, 페이지 수, URL, 시간대 등
- `user.yml`: 로그인 계정 정보

`SECRET_KEY`, `aes_key`, 사용자 비밀번호와 같은 민감한 값은 운영 환경에 맞게 안전하게 설정해야 합니다. 실제 설정 파일은 저장소에 커밋하지 않습니다.

### 문서 경로

Markdown 문서는 기본적으로 `data/pages` 아래에서 관리합니다.

외부 폴더를 사용하려면 해당 경로를 `data/pages`에 심볼릭 링크로 연결할 수 있습니다. 데이터베이스는 기본 설정에서 `data/db.sqlite`에 생성됩니다.

### 파일 감시 방식

`config.py`의 `WATCHDOG_OBSERVER`로 파일 감시 방식을 선택할 수 있습니다.

```python
WATCHDOG_OBSERVER = "native"
```

- `native`: 일반적인 로컬 파일 시스템
- `polling`: WSL2 또는 네트워크·동기화 폴더처럼 기본 파일 이벤트 감지가 불안정한 환경

## 개발 서버 실행

```shell
python main.py
```

기본 접속 주소:

```text
http://127.0.0.1:5000
```

Flask 개발 서버는 로컬 개발과 기능 확인 용도로만 사용합니다.

## Gunicorn으로 실행

Gunicorn은 Linux, WSL 또는 컨테이너 환경에서 실행할 수 있습니다. Windows에서는 직접 지원되지 않습니다.

프로젝트 루트에서 다음 명령을 실행합니다.

```shell
gunicorn \
  --bind 127.0.0.1:8000 \
  --workers 1 \
  --threads 4 \
  --access-logfile - \
  --error-logfile - \
  main:app
```

접속 주소:

```text
http://127.0.0.1:8000
```

`main.py`를 불러올 때 문서 변경 감시기도 함께 시작됩니다. 여러 worker를 사용하면 감시기가 중복 실행될 수 있으므로 현재 구조에서는 `--workers 1`을 권장합니다. 동시 요청은 `--threads` 값으로 처리할 수 있습니다.

외부에 서비스를 공개할 때는 Gunicorn 앞에 Nginx 등의 리버스 프록시를 두고 HTTPS를 적용하는 것을 권장합니다. 외부 접속을 직접 허용해야 한다면 바인딩 주소를 다음과 같이 변경할 수 있습니다.

```shell
gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 4 main:app
```

방화벽과 접근 제어가 준비되지 않은 환경에서는 `0.0.0.0`으로 실행하지 마세요.

## 문서 메타데이터

문서 상단의 frontmatter에서 공개 범위와 게시 여부 등을 설정할 수 있습니다.

```markdown
---
Created: 2026-07-20 12:00:00
Permission: 2
Posted: 1
Pinned: 0
Tags: note, obsidian
Summary: 문서 요약
---
```

### Permission

- `0`: 비공개
- `1`: 링크를 가진 사용자에게만 공개
- `2`: 전체 공개

### Posted

- `0`: 게시물 목록에 노출하지 않음
- `1`: 게시물 목록에 노출

### Pinned

- `0`: 일반 정렬
- `1`: 게시물 목록 최상단에 고정

## 테스트

```shell
python -m unittest discover -s tests -v
```
