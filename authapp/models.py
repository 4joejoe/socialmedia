from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    PermissionsMixin,
)
from django.db import models

# Create your models here.


class CustomAccountManger(BaseUserManager):

    def create_superuser(self, email, username, first_name, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)
        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")

        return self.create_user(email, username, first_name, password, **other_fields)

    def create_user(self, email, username, first_name, password, **other_fields):
        if not email:
            raise ValueError("You must provide an email address.")
        if not username:
            raise ValueError("You must provide a username.")
        email = self.normalize_email(email)
        user = self.model(
            email=email, username=username, first_name=first_name, **other_fields
        )
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = CustomAccountManger()
    friends = models.ManyToManyField("self", blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name"]

    # groups = models.ManyToManyField(Group, related_name="custom_users")

    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    def send_friend_request(self, to_user):
        if to_user != self:
            FriendRequest.objects.create(from_user=self, to_user=to_user)

    def pending_friend_requests(self):
        return FriendRequest.objects.filter(to_user=self)

    def remove_friend_request(self, from_user):
        FriendRequest.objects.filter(from_user=from_user, to_user=self).delete()

    def accept_friend_request(self, from_user):
        friend_request = FriendRequest.objects.filter(
            from_user=from_user, to_user=self
        ).first()
        if friend_request:
            self.friends.add(from_user)
            from_user.friends.add(self)
            friend_request.delete()

    def reject_friend_request(self, from_user):
        FriendRequest.objects.filter(from_user=from_user, to_user=self).delete()

    def __str__(self):
        return self.username


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        CustomUser, related_name="requests_sent", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        CustomUser, related_name="requests_received", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )  # when the friend request was created

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"
