from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from oj_objective.views import (
    auto_fill_explanations_with_ai,
    cleanup_option_text,
    cleanup_question_content,
    normalize_ai_question,
)


class ObjectiveMarkdownFormatTests(SimpleTestCase):
    def test_cleanup_question_content_wraps_cpp_block(self):
        content = (
            '下面代码执行后，输出是()。\n'
            '1 a = 3;\n'
            '2 b = a = 4;\n'
            '3 printf("%d %d", a, b);\n'
            'A. 4 4'
        )

        cleaned = cleanup_question_content(content, [{'key': 'A', 'text': '4 4'}])

        self.assertIn('```cpp', cleaned)
        self.assertIn('a = 3;', cleaned)
        self.assertIn('printf("%d %d", a, b);', cleaned)
        self.assertNotIn('A. 4 4', cleaned)

    def test_cleanup_question_content_wraps_inline_expression(self):
        content = 'C++表达式 2 + 3 * 4 % 5 的值为()。'
        cleaned = cleanup_question_content(content, [])
        self.assertIn('`2 + 3 * 4 % 5`', cleaned)

    def test_cleanup_option_text_wraps_multiline_cpp_block(self):
        option_text = '1 | N = N - M\n2 | M = M - N'
        cleaned = cleanup_option_text(option_text)

        self.assertIn('```cpp', cleaned)
        self.assertIn('N = N - M', cleaned)
        self.assertIn('M = M - N', cleaned)
        self.assertNotIn('1 |', cleaned)

    def test_normalize_ai_question_wraps_option_code(self):
        raw_q = {
            'question_type': 'single',
            'content': '下面代码输出是()',
            'options': [
                {'key': 'A', 'text': '4 4'},
                {'key': 'B', 'text': '3 3'},
                {'key': 'C', 'text': '都不正确'},
            ],
            'correct_answers': ['A'],
            'explanation': 'printf("%d %d", a, b);',
        }

        normalized = normalize_ai_question(raw_q, 1)
        option_map = {item['key']: item['text'] for item in normalized['options']}

        self.assertEqual(option_map['A'], '`4 4`')
        self.assertEqual(option_map['B'], '`3 3`')
        self.assertEqual(option_map['C'], '都不正确')
        self.assertIn('`printf("%d %d", a, b);`', normalized['explanation'])

    def test_normalize_ai_question_wraps_multiline_option_cpp_block(self):
        raw_q = {
            'question_type': 'single',
            'content': '选择执行效果正确的一项',
            'options': [
                {'key': 'A', 'text': '1 | N = N - M\n2 | M = M - N'},
                {'key': 'B', 'text': '普通文本'},
            ],
            'correct_answers': ['A'],
        }

        normalized = normalize_ai_question(raw_q, 1)
        option_map = {item['key']: item['text'] for item in normalized['options']}

        self.assertTrue(option_map['A'].startswith('```cpp'))
        self.assertIn('N = N - M', option_map['A'])
        self.assertIn('M = M - N', option_map['A'])
        self.assertEqual(option_map['B'], '普通文本')

    @override_settings(DEEPSEEK_API_KEY='test-key', OBJECTIVE_EXPLANATION_AI_TIMEOUT=20)
    @patch('oj_objective.views.call_deepseek')
    def test_auto_fill_explanations_with_ai(self, mock_call):
        mock_call.return_value = (
            '{"items":[{"order":1,"explanation":"因为 `2 + 3 * 4 % 5` 的结果是 4，所以选 A。"}]}',
            {},
        )
        questions = [
            {
                'order': 1,
                'question_type': 'single',
                'content': 'C++表达式 2 + 3 * 4 % 5 的值为()。',
                'options': [
                    {'key': 'A', 'text': '`4`'},
                    {'key': 'B', 'text': '`14`'},
                ],
                'correct_answers': ['A'],
                'explanation': '',
            }
        ]

        auto_fill_explanations_with_ai(questions)

        self.assertTrue(questions[0]['explanation'])
        self.assertIn('`2 + 3 * 4 % 5`', questions[0]['explanation'])

    @override_settings(DEEPSEEK_API_KEY='test-key', OBJECTIVE_EXPLANATION_AI_TIMEOUT=20)
    @patch('oj_objective.views.call_deepseek')
    def test_auto_fill_explanations_with_ai_keeps_existing(self, mock_call):
        questions = [
            {
                'order': 1,
                'question_type': 'single',
                'content': '题干',
                'options': [{'key': 'A', 'text': '1'}],
                'correct_answers': ['A'],
                'explanation': '已有解析',
            }
        ]

        auto_fill_explanations_with_ai(questions)

        mock_call.assert_not_called()
        self.assertEqual(questions[0]['explanation'], '已有解析')
