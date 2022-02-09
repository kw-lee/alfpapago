alfpapago : Papago Translation Workflow for Alfred
==============

Papago Translation Workflow for Alfred

Alfred에서 네이버 파파고 번역을 실시하는 워크플로우

Install workflow
--------------
 `NaverPapago.alfredworkflow`를 다운로드 받아서 실행한다.

Usage
--------------
* `papago {query}` {query} 자리에 원하는 문장을 입력하면 파파고 번역 결과와 원본 텍스트를 복사하실 수 있습니다.

Build
--------------
```bash
bash ./make.sh
```

Requirements
--------------

* python3
  * [alfred-workflow-py3](https://github.com/kw-lee/alfred-workflow-py3.git)
  * requirements.txt

```bash
git submodule update --init --recursive
pip install -r requirements.txt -t workflow/lib
```

LICENSE
--------------
 - MIT