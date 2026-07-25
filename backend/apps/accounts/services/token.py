from django.conf import settings
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

def create_token(user_obj):
    signer = TimestampSigner()
    token = signer.sign(user_obj.pk)
    return token


def get_user_pk_from_token(token):
    signer = TimestampSigner()
    max_age = settings.EMAIL_TOKEN_DURATION
    try:
        user_pk = signer.unsign(token, max_age=max_age)
        return user_pk
    except (SignatureExpired, BadSignature):
        return None


def revoke_user_tokens(user_obj) -> int:
    blacklisted_count = 0
    for outstanding_token in OutstandingToken.objects.filter(user=user_obj):
        _, created = BlacklistedToken.objects.get_or_create(token=outstanding_token)
        if created:
            blacklisted_count += 1
    return blacklisted_count