from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from tags.models import Tag, UserTag
from authn.decorators.api import api
from club.exceptions import ApiAccessDenied
from users.models.user import User


def api_profile_user(request, user_slug):
    if user_slug == "me":
        user_slug = request.me.slug

    user = get_object_or_404(User, slug=user_slug)

    if request.me.moderation_status != User.MODERATION_STATUS_APPROVED and request.me.id != user.id:
        raise ApiAccessDenied(title="Non-approved users can only access their own profiles")

    return user

@api(require_auth=True)
def api_profile(request, user_slug):
    user = api_profile_user(request, user_slug)

    return JsonResponse({
        "user": user.to_dict()
    })

@api(require_auth=True)
def api_profile_tags(request, user_slug):
    user = api_profile_user(request, user_slug)

    return JsonResponse({
        "tags": [tag.tag.code for tag in UserTag.objects.filter(user=user)],
    })


@api(require_auth=True)
def api_profile_by_telegram_id(request, telegram_id):
    user = get_object_or_404(User, telegram_id=telegram_id)

    return JsonResponse({
        "user": user.to_dict()
    })
