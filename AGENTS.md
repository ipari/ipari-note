# AGENTS.md

## 프로젝트 개요

`ipari-note`는 개인 노트 겸 블로그 애플리케이션입니다. 
- Obsidian으로 관리하는 로컬 마크다운 문서를 웹에서 작성, 편집, 열람할 수 있게 합니다.
- 문서 변경을 감지해 렌더링하고 DB에 저장합니다.
- 문서별 공개 범위를 유연하게 관리할 수 있습니다.

## 작동 흐름

- `main.py`가 Flask 앱을 만들고 `PageWatcher`를 별도 데몬 스레드로 실행합니다.
- `app/__init__.py`의 `create_app()`이 설정 로드, 블루프린트 등록, DB 초기화, 설정/사용자 동기화를 수행합니다.
- 노트 원본은 기본적으로 `data/pages` 아래의 `.md` 파일입니다.
- `app/note/note.py`가 마크다운 렌더링, 메타데이터 파싱, DB 업데이트, 페이지/파일 서빙, 피드 생성을 담당합니다.
- `app/note/markdown.py`에는 Python-Markdown 확장, Obsidian 스타일 위키링크/이미지 임베드, YAML 유사 메타데이터, 한글 slug 처리 등 커스텀 마크다운 동작을 담당합니다.
- 기본 테마는 `themes/yaong`이며 템플릿과 정적 파일이 이곳에 있습니다.

### frontmatter

`ipari-note`는 frontmatter의 다음 속성을 사용합니다.
- `Permission`
  - 0: 로그인한 사용자만 볼 수 있음
  - 1: 링크를 가진 사람만 볼 수 있음
  - 2: 모두가 볼 수 있음
- `Pinned`
  - 1: 목록의 최상단에 고정
- `Posted`
  - 1: 포스트 목록에 노출됨


## 환경과 실행

이 프로젝트는 Python Flask 애플리케이션입니다.
Linux, MacOS, WSL2 등 여러 환경에서 작동을 보장해야합니다.

의존성은 `requirements.txt`를 기준으로 설치합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

런타임에는 저장소 루트에 다음 파일이 필요합니다. 실제 파일은 `.gitignore` 대상이며 샘플은 `*.bak`로 제공됩니다.

- `config.py`: Flask secret, SQLAlchemy DB URI, watchdog 모드 등
- `config.yml`: 노트 제목, 테마, 페이지 수, URL, timezone, AES key 등
- `user.yml`: 사용자 이메일, 이름, 비밀번호 해시
- `data/pages`: 마크다운 노트 원본 디렉터리

샘플을 복사해 로컬에서 실행할 수 있습니다.

```bash
cp config.py.bak config.py
cp config.yml.bak config.yml
cp user.yml.bak user.yml
mkdir -p data/pages
python3 main.py
```

`main.py`는 watcher 스레드를 함께 띄웁니다. 단순 라우팅/렌더링 테스트나 모듈 단위 확인에서는 전체 앱 부팅보다 필요한 모듈을 스텁으로 격리하는 편이 안전합니다.

## 테스트

현재 테스트는 `unittest` 기반이며 `pytest`로도 실행할 수 있는 형태입니다.

```bash
python3 -m unittest discover -s tests
```

### 테스트 파일

- `tests/test_markdown.py`: `app/note/markdown.py`를 직접 로드하고 `Config`를 스텁 처리해 마크다운 확장 동작을 검증합니다.
- `tests/test_tags.py`: `app/main/view.py`를 직접 로드하고 노트/사용자 의존성을 스텁 처리해 중첩 태그 라우팅을 검증합니다.

마크다운 파서, 라우팅 규칙, 태그/메타데이터 파싱, 권한 처리처럼 사용자 노트 URL이나 렌더링 결과가 바뀌는 작업에는 회귀 테스트를 추가하거나 갱신하세요.

## 작업 지침

- 기존 구조와 스타일을 우선 따른다.
- 불필요한 대규모 리팩토링은 피한다. 하지만 정말 필요하다고 생각되면 제안한다.
- 주석은 영어로 작성한다.