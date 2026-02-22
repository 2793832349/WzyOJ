from oj_problem.views import _normalize_statement_text, _extract_markdown_sections
from oj_problem.models import Problem

updated = []
for p in Problem.objects.all():
    try:
        raw = p.description or ''
        norm = _normalize_statement_text(raw)
        sections = _extract_markdown_sections(norm)
        input_fmt = (sections.get('input_format') or '').strip()
        output_fmt = (sections.get('output_format') or '').strip()
        desc = sections.get('description') or ''
        # If description is empty, use background/hint as fallback
        if not desc:
            desc = '\n\n'.join([sections.get(k, '') for k in ('background', 'description', 'hint') if sections.get(k)])
        changed = False
        if input_fmt and (not getattr(p, 'input_format', None)):
            p.input_format = input_fmt
            changed = True
        if output_fmt and (not getattr(p, 'output_format', None)):
            p.output_format = output_fmt
            changed = True
        # Update description only if it appears to be samples-only or different
        if desc and desc.strip() and desc.strip() != p.description.strip():
            p.description = desc.strip()
            changed = True
        if changed:
            p.save()
            updated.append(p.id)
    except Exception as e:
        print('failed for', p.id, e)

print('updated', updated)
