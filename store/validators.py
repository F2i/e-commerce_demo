from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class FileSizeValidator:
    message = _(
        'File size must less than or equal to %(max_file_size)sMB'
    )
    code = 'invalid_file_size'

    def __init__(self, max_file_size_mb, message=None, code=None):
        self.max_file_size_mb = max_file_size_mb
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        if value.size > self.max_file_size_mb*1024**2:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    'max_file_size': self.max_file_size_mb,
                    'value': value,
                }
            )

def validate_file_size(file):
    return