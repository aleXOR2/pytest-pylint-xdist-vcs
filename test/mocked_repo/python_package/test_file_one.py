'''Test module docstring'''
import json
import pprint


def test_uno():
    '''Test function uno docstring'''
    json_str = '''{
        "info": {
            "author": "The Python Packaging Authority",
            "author_email": "pypa-dev@googlegroups.com",
            "home_page": "https://github.com/pypa/sampleproject",
            "classifiers": ["Development Status :: 5 - Stable"]
        }
    }'''
    project_info = json.loads(json_str)['info']
    assert project_info['author_email'] == 'pypa-dev@googlegroups.com'


def test_dos(capsys):
    '''Test function dos docstring'''
    verses = [
        'We have all received an education',
        'In something', 'somehow', 'have we not?',
        'So thank the Lord that in this nation',
        'A little learning means a lot.',
        'Onegin was, so some decided',
        'A learned, if not pedantic, sort'
    ]
    pprint.pprint(verses)
    captured = capsys.readouterr()
    assert   captured.out == \
    '''['We have all received an education',
 'In something',
 'somehow',
 'have we not?',
 'So thank the Lord that in this nation',
 'A little learning means a lot.',
 'Onegin was, so some decided',
 'A learned, if not pedantic, sort']
'''
