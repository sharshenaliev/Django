from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.utils.timezone import now


class CustomAccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password, organization):
        user = self.model(email=email, first_name=first_name, last_name=last_name, password=password, organization=organization)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password, first_name, last_name):
        user = self.create_user(email=email, first_name=first_name, last_name=last_name, password=password,
                                organization=Organization.objects.create(title='Admin', email='admin@localhost'))
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.username = 'admin'
        user.save(using=self.db)
        return user

    def get_by_natural_key(self, email_):
        print(email_)
        return self.get(email=email_)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True, db_index=True,
                              validators=[EmailValidator(allowlist=['gmail.com'])])
    date_joined = models.DateTimeField(default=now())
    is_staff = models.BooleanField(default=False)
    lateness = models.IntegerField(default=0)
    betimes = models.IntegerField(default=0)
    organization = models.ForeignKey('Organization', on_delete=models.PROTECT, related_name='organization_title_set')
    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'

    objects = CustomAccountManager()

    def get_short_name(self):
        return self.first_name

    def natural_key(self):
        return self.email

    def __str__(self):
        return self.email


class Organization(models.Model):
    title = models.CharField(max_length=50, unique=True, db_index=True)
    email = models.EmailField(max_length=50, unique=True)
    start_time = models.TimeField(editable=True, null=True)
    end_time = models.TimeField(editable=True, null=True)

    def __str__(self):
        return self.title


class Time(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='time', null=True)
    date = models.DateField(auto_now_add=True)
    start_time = models.DateTimeField(default=now())
    end_time = models.DateTimeField(null=True)
    day = models.DurationField(null=True)


class Profile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='month', null=True)
    date = models.DateField(auto_now_add=True)
    month = models.DurationField(null=True)
