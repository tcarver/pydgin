from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class AuthTestPermissionManager(models.Manager):
    def get_query_set(self):
        return super(AuthTestPermissionManager, self).\
            get_query_set().filter(content_type__name='auth_test_perms')


class AuthTestPermission(Permission):
    """ AuthTestPermission not attached to a model"""

    objects = AuthTestPermissionManager()

    class Meta:
        proxy = True
        verbose_name = "auth_test_perms"

    def save(self, *args, **kwargs):
        ct, created = ContentType.objects.get_or_create(
            model=self._meta.verbose_name, app_label=self._meta.app_label,
        )
        print("Status of " + self._meta.verbose_name + " is  " + created)
        self.content_type = ct
        super(AuthTestPermission, self).save(*args, **kwargs)
