CODEQL_DB_PATH = 'codeql-db'

CODEQL_QL_PATH = '/codeql/codeql-repo/javascript/ql/src/Security/'

CODEQL_CREATE_COMMAND = 'codeql database create --language=python --overwrite {db_path} --source-root={src_path}'

CODEQL_ANALYSIS_COMMAND = 'codeql database analyze {db_path} {ql_path} --format=csv --output={output_path} --threads=4'