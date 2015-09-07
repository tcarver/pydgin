class DefaultRouter(object):
    """
    A router to control all database operations on models in the
    default application.
    """
    def db_for_read(self, model, **hints):
        """
        Read always go to default.
        """
        return "default"

    def db_for_write(self, model, **hints):
        """
        Writes always go to default.
        """
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the default pool.
        """
        db_list = ('default')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        return True
