# import re
# from django.core.exceptions import ValidationError

# class CharacterPasswordValidator:
#     def validate(self, password, user=None):
#         if not re.search(r'[a-z]', password):
#             raise ValidationError("Must include lowercase letter")
#         if not re.search(r'[A-Z]', password):
#             raise ValidationError("Must include uppercase letter")
#         if not re.search(r'[0-9]', password):
#             raise ValidationError("Must include digit")
#         if not re.search(r'[^a-zA-Z0-9]', password):
#             raise ValidationError("Must include symbol")

#     def get_help_text(self):
#         return "Password must include lowercase letter, uppercase letter, digit, and symbol"