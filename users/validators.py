from django.core.exceptions import ValidationError

class Validator:
    def validate_email(self, email):
        if '@' not in email:
            raise ValidationError('Email must contain @')

    def validate_password(self, password):
        if len(password) < 8:
            raise ValidationError('Minimum length of password should be 8')