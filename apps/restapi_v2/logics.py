from rest_framework_simplejwt.tokens import RefreshToken
from apps.restapi_v2 import tasks as restapi_v2_tasks
from apps.users import models as user_models
from rest_framework.exceptions import NotFound, ValidationError
from apps.companies import models as company_models


def user_send_sms_code(user: user_models.User) -> None:
    try:
        phone = user.phone
        message = f'Your code - {user.sms_code}'
        restapi_v2_tasks.send_sms.delay(phone, message)
    except Exception as e:
        pass  # TODO: Поставить логирования


def get_tokens_for_user(user: user_models.User) -> dict:

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def get_cafe(cafe_id: int) -> company_models.Cafe:
    try:
        cafe = company_models.Cafe.objects.get(pk=cafe_id)
        return cafe
    except company_models.Cafe.DoesNotExist:
        raise NotFound('Cafe does not exist')


def get_user_phone(phone: str) -> user_models.User:
    try:
        user = user_models.User.objects.get(phone=phone)
        return user
    except user_models.User.DoesNotExist:
        raise NotFound('invalid phone user does not exist')

