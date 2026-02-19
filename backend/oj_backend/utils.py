import logging

from rest_framework.views import exception_handler as base_exception_handler
from rest_framework.exceptions import ValidationError


logger = logging.getLogger(__name__)


def exception_handler(exception, context):
    response = base_exception_handler(exception, context)
    if response is None:
        request = context.get('request')
        logger.exception(
            "Unhandled exception in DRF",
            extra={
                'path': getattr(request, 'path', None),
                'method': getattr(request, 'method', None),
                'view': str(context.get('view', None)),
            },
        )
    if response is not None and isinstance(exception, ValidationError):
        if isinstance(response.data, dict):
            data = {}
            for key, value in response.data.items():
                if not isinstance(key, str):
                    data = response.data
                    break
                if isinstance(value, list):
                    data[key] = ';'.join(map(str, value))
                else:
                    data[key] = str(value)
            detail = data.pop('non_field_errors', None)
            if detail:
                data['detail'] = detail
            response.data = data
        elif isinstance(response.data, list):
            response.data = {'detail': ';'.join(response.data)}
    return response
