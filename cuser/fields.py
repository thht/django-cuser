from django.conf import settings


try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


from django.db.models.fields.related import ForeignKey, ManyToOneRel
from cuser.middleware import CuserMiddleware


if 'cuser' not in settings.INSTALLED_APPS:
    raise ValueError("Cuser middleware is not enabled")


# Register fields with south, if installed
if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^cuser\.fields\.CurrentUserField"])


class CurrentUserField(ForeignKey):
    def __init__(self, to_field=None, rel_class=ManyToOneRel, **kwargs):
        self.add_only = kwargs.pop('add_only', False)
        kwargs.update({
          'editable': False,
          'null': True,
          'rel_class': rel_class,
          'to': User,
          'to_field': to_field,
        })
        super(CurrentUserField, self).__init__(**kwargs)

    def pre_save(self, model_instance, add):
        if add or not self.add_only:
            user = CuserMiddleware.get_user()
            if user:
                setattr(model_instance, self.attname, user.pk)
                return user.pk
        return super(CurrentUserField, self).pre_save(model_instance, add)
