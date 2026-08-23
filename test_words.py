import sys
sys.path.insert(0, 'generation')
sys.path.insert(0, 'tests')
from verifier import _check_has_content
from fixtures import SUPPORTED_ANSWER_TEXT
body=SUPPORTED_ANSWER_TEXT.split('Sources:')[0].strip()
print('Words:', len(body.split()))
print(_check_has_content(SUPPORTED_ANSWER_TEXT))
