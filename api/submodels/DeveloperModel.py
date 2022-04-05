from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class DeveloperManager(BaseUserManager):
    def create_user(self, name, email, password, organisation):
        if not email:
            raise ValueError("Please provide us your email")
        email = self.normalize_email(email)
        developer = self.model(email = email, name = name, organisation = organisation)
        developer.set_password(password)
        developer.save(using = self._db)
        return developer
    
    def create_superuser(self, name, email, password, organisation):
        creator = self.create_user(name, email, password, organisation)
        creator.is_superuser = True
        creator.is_staff = True
        creator.save(using = self._db)
        return creator

class DeveloperModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique = True, max_length = 255, null=True)
    name = models.CharField(max_length = 255, null=True)
    organisation = models.CharField(max_length=255, null=True)
    is_staff = models.BooleanField(default = False)

    objects = DeveloperManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'organisation']