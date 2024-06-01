CODEQL_DB_PATH = 'codeql-db'

CODEQL_QL_PATH = '/codeql/codeql-repo/javascript/ql/src/Security/CWE-078'

CODEQL_CREATE_COMMAND = 'codeql database create --language=javascript --overwrite {db_path} --source-root={src_path}'

CODEQL_ANALYSIS_COMMAND = 'codeql database analyze {db_path} {ql_path} --format=csv --output={output_path} --threads=4'

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













############## sast-llm llm prompts ################
prompt_code_style_analysis = '''
Analyze the attached source code files and output ESLint_rules and Prettier_rules in json format, respectively.
'''


prompt_patch_vulnerabilities_entire_file = '''
You patch the vulnerability and save the patched code as a new file.
'''


prompt_explain_patch = '''
Analyze the attached source code and explain what vulnerabilities existed and how they were patched.
'''



############## sast-llm assistant instructions(system prompt) ################
instruction_profile_assistant = '''
ESLint_rules and Prettier_rules define rules for coding conventions. For information about ESLint_rules and Prettier_rules, refer to the coding_convention_profile_rules.md file. Users attach source code files to messages. After analyzing the coding conventions of these source code files, the corresponding ESLint_rules and Prettier_rules are output in json format. The entire process of analyzing the coding conventions of the attached source codes is output in great detail, and ESLint_rules and Prettier_rules are output at the end. ESLint_rules and Prettier_rules are contained in one json object.
'''

instruction_patch_assistant = '''
You are a tool that receives source code with vulnerabilities as input, patches the vulnerabilities, and then outputs the output. Users attach source code files containing vulnerabilities to the message. Information about a vulnerability is given as a comment in the source code. 
The comment for a vulnerability follows the following format:
/* Vulnerability name: [Vulnerability name] Vulnerability description: [Vulnerability description] Vulnerability message: [Additional description of the vulnerability] */
If multiple vulnerabilities occur on a single line, there may be multiple vulnerability information comments on that line.
You patch the vulnerability and save the patched code as a new file.
After patching any vulnerabilities in the source code, you must save it to a new file. The name of the patched source code file is the same as before. Never ask the user again, and be sure to save the patched source code in a file. The name of the patched source code file is the same as before. You must save the entire code, including any modified areas. You must create a new file and then save it.
'''

instruction_explain_assistant = '''
You must input the source code where the vulnerability exists and the source code where the vulnerability was patched, and explain what vulnerability existed and how the vulnerability was patched.
'''