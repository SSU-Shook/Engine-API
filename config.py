CODEQL_DB_PATH = 'codeql-db'

# CODEQL_QL_PATH = '/codeql/codeql-repo/javascript/ql/src/Security/'
CODEQL_QL_PATH = '/codeql/codeql-repo/javascript/ql/src/Security/CWE-078'

CODEQL_CREATE_COMMAND = 'codeql database create --language=javascript --overwrite {db_path} --source-root={src_path}'

CODEQL_ANALYSIS_COMMAND = 'codeql database analyze {db_path} {ql_path} --format=csv --output={output_path} --threads=16'

TEMPLATE = '''
# {title}

## 프로젝트 개요

- 분석 날짜: {date}
- 언어: JavaScript
- 프레임워크: NPM Library
- 코드 패치 LLM 모델: {model}

## 취약점 분석 결과

### 0. 취약점 분석 통계   

- 전체 발견 취약점: {vuln_count}
- 심각도별 취약점   
    - error: {error_count}
    - warning: {warning_count}
    - note : {note_count}

{details}
'''.strip()

VULN_DETAIL = '''
### {idx}. {vuln_name}
- 코드 경로: `{path}`
   
- 심각도: {severity}
   
- 설명: {description}
   
- 메시지: `{message}`
     
- 원본 코드   
```js
{original_code}
```
   
- 패치 코드   
```js
{patched_code}
```
   
- 코드 비교   
```diff
{diff_code}
```
   
- 코드 패치 설명  
    - {patch_description}
'''.strip()
