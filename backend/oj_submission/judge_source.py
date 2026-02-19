from oj_problem.models import JudgeModeChoices, Problem


def _get_template(problem: Problem, language: str) -> dict:
    templates = problem.leetcode_templates or {}
    template = templates.get(language, {}) if isinstance(templates, dict) else {}
    if not isinstance(template, dict):
        return {'prepend': '', 'append': ''}
    return {
        'prepend': str(template.get('prepend', '')),
        'append': str(template.get('append', '')),
    }


def build_judge_source(problem: Problem, language: str, source: str) -> str:
    source = source or ''
    if problem.judge_mode != JudgeModeChoices.LEETCODE:
        return source

    template = _get_template(problem, language)
    prepend = template['prepend']
    append = template['append']
    return f"{prepend}{source}{append}"


def get_language_starter(problem: Problem, language: str) -> str:
    templates = problem.leetcode_templates or {}
    template = templates.get(language, {}) if isinstance(templates, dict) else {}
    if not isinstance(template, dict):
        return ''
    return str(template.get('starter', ''))
