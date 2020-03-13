노트의 문서는 [Markdown](https://daringfireball.net/projects/markdown/syntax) 문법을 기반으로 합니다.
기본 문법과 확장 문법을 구분하지 않고 서술합니다.

[목차]

## 서식

```markdown
**굵은** 글자
*기울어진* 글자
[[Home]]으로 가는 노트 내부 링크 걸기
[구글](https://google.com)로 링크 걸기
![이미지](sample_image.png)
```

**굵은** 글자
*기울어진* 글자
[[Home]]으로 가는 노트 내부 링크 걸기
[구글](https://google.com)로 링크 걸기
![이미지](sample_image.png)


## 헤더
최상위 헤더 `<h1>` 에는 표제어가 자동으로 삽입됩니다.
따라서 본문에는 `<h2>` 이후의 헤더를 사용합니다.

```markdown
## <h2> 태그
### <h3> 태그
#### <h4> 태그
```

## 표

```markdown
| 번호 | 제목 | 가수 |
| :---: | :---: | :---: |
| 46130 | fantastic baby | 하현우 |
| 46732 | Lazenca, save us | 하현우 |
| 62056 | endless | 플라워 |
```

| 번호 | 제목 | 가수 |
| :---: | :---: | :---: |
| 46130 | fantastic baby | 하현우 |
| 46732 | Lazenca, save us | 하현우 |
| 62056 | endless | 플라워 |


## 목차
문서에 `[목차]` 를 넣으면, 해당 위치에 헤더를 기반으로 목차를 생성합니다.


## 주석
아래와 같은 방식으로 사용합니다.

```markdown
주석[^1]은 이렇게[^이렇게] 사용합니다.

[^1]: '주석'에 달린 주석
[^이렇게]: '이렇게'에 달린 주석
```

주석[^1]은 이렇게[^이렇게] 사용합니다.

[^1]: '주석'에 달린 주석
[^이렇게]: '이렇게'에 달린 주석


## 코드

### 코드 블럭

````markdown
```python
def blah():
    return 'blah'
```
````

```python
def blah():
    print('blah')
    return 'blah'
```

코드 블럭 안에 코드 블럭을 넣으려면 상위 블럭에 `` ` ``를 한개 더 넣으세요. 

### 코드 라인 강조

````markdown
```python hl_lines="1 3"
def blah():
    print('blah')
    return 'blah'
```
````

```python hl_lines="1 3"
def blah():
    print('blah')
    return 'blah'
```

## 안내
안내하고 싶은 내용이 있을 때, 상자 모양으로 강조하여 알려줄 수 있습니다.

```markdown
!!! tip "차가운 맥주가 없을 땐"
    급한 상황에 차갑게 해 놓은 맥주가 없을 땐 맥주에 얼음을 넣어 마시면 된다.
```

!!! tip "차가운 맥주가 없을 땐"
    급한 상황에 차갑게 해 놓은 맥주가 없을 땐 맥주에 얼음을 넣어 마시면 된다.
    
info, help, tip, todo, important, alert 를 사용할 수 있습니다. 각 유형의 생김새는 [[ipari-note/admonition]] 페이지를 참고해주세요.

위의 항목 이외에 어떤 유형이든 사용할 수 있습니다. 대신 이 경우 스타일이 정의되어있지 않으므로, css에 스타일을 정의하고 사용해야 합니다.
