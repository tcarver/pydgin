from django.test import TestCase
from django.db import router
from django.contrib.auth.models import User, Group, Permission
from django.test.client import RequestFactory, Client
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import authenticate


class AuthTestCase(TestCase):

    multi_db = True

    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.group = Group.objects.get_or_create(name='READ')
        self.user = User.objects.create_user(
            username='test_user', email='test@test.com', password='test_pass')

    def test_create_groups(self):
        # test if we get back the READ group without creating it
        read_group, created = Group.objects.get_or_create(name='READ')
        self.assertEqual(read_group.name, "READ")
        self.assertEqual(created, False)

        dil_group, created = Group.objects.get_or_create(name='DIL')
        self.assertEqual(dil_group.name, "DIL")
        self.assertTrue(created)

        curator_group, created = Group.objects.get_or_create(name='CURATOR')
        self.assertEqual(curator_group.name, "CURATOR")
        self.assertTrue(created)

        pydgin_admin_group, created = Group.objects.get_or_create(name='PYDGIN_ADMIN')
        self.assertEqual(pydgin_admin_group.name, "PYDGIN_ADMIN")
        self.assertTrue(created)

    def test_users_groups_perms(self):
        read_group = Group.objects.get(name='READ')
        read_user = User.objects.create_user(
            username='test_read', email='test_read@test.com', password='test123')
        read_user.groups.add(read_group)
        self.assertTrue(read_user.groups.filter(name='READ').exists())

        dil_group, created = Group.objects.get_or_create(name='DIL')
        self.assertTrue(created)
        dil_user = User.objects.create_user(
            username='test_dil', email='test_dil@test.com', password='test123')
        dil_user.groups.add(dil_group)
        self.assertTrue(dil_user.groups.filter(name='DIL').exists())

        all_groups_of_dil_user = dil_user.groups.values_list('name', flat=True)
        self.assertTrue("DIL" in all_groups_of_dil_user, "Found DIL in groups")
        self.assertTrue("READ" in all_groups_of_dil_user, "Found READ in groups")

        # create the content type
        content_type, created = ContentType.objects.get_or_create(
            model="auth_test_perms", app_label="auth_test",
        )

        # create permission and assign ...Generally we create via admin interface
        Permission.objects.create(codename='can_read', name='Can Read Data', content_type=content_type)
        can_read_permission = Permission.objects.get(codename='can_read')
        read_user.user_permissions.add(can_read_permission)
        self.assertTrue(read_user.has_perm('auth_test.can_read'))

    def test_routers(self):
        self.original_routers = router.routers

        routers = []
        for router_ in self.original_routers:
            routers.append(router_.__class__.__name__)

        self.assertTrue('AuthRouter' in routers, "Found AuthRouter in routers")
        self.assertTrue('DefaultRouter' in routers, "Found DefaultRouter in routers")

    def test_login_perms(self):
        user = authenticate(username="test_user", password="test_wrong_pass")
        self.assertTrue(user is None, "Authentication failed")

        user = authenticate(username="test_user", password="test_pass")
        self.assertTrue(user is not None, "Authentication passed")
        self.assertTrue(user.is_authenticated(), "Authentication passed")
