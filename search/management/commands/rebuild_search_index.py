import logging

from django.core.management import BaseCommand

from comments.models import Comment
from posts.models.post import Post
from search.models import SearchIndex
from users.models.user import User
from utils.queryset import chunked_queryset

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Rebuild search index for posts and users"

    def handle(self, *args, **options):
        SearchIndex.objects.all().delete()

        for chunk in chunked_queryset(
            Comment.visible_objects().filter(is_deleted=False, post__is_visible=True).order_by("-created_at")
        ):
            for comment in chunk:
                self.stdout.write(f"Indexing comment: {comment.id}")
                SearchIndex.update_comment_index(comment)

        for chunk in chunked_queryset(
            Post.visible_objects().filter(is_shadow_banned=False).order_by("-created_at")
        ):
            for post in chunk:
                self.stdout.write(f"Indexing post: {post.slug}")
                SearchIndex.update_post_index(post)

        for chunk in chunked_queryset(
            User.objects.filter(moderation_status=User.MODERATION_STATUS_APPROVED).order_by("-created_at")
        ):
            for user in chunk:
                self.stdout.write(f"Indexing user: {user.slug}")
                SearchIndex.update_user_index(user)
                SearchIndex.update_user_tags(user)

        self.stdout.write("Done 🥙")
