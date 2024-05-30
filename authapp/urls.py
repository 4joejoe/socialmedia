from django.urls import path
from .views import (
    FriendRequestResponseView,
    FriendsListView,
    PendingRequestsView,
    UserSearchView,
    UserView,
    FriendRequestView,
)

urlpatterns = [
    path(
        "user/<int:user_id>/delete/",
        UserView.as_view(),
        name="user-delete",
    ),
    path(
        "user/<int:user_id>/update/",
        UserView.as_view(),
        name="user-update",
    ),
    path("user/", UserView.as_view()),
    path(
        "user/<int:user_id>/logout/",
        UserView.as_view(),
        name="user-logout",
    ),
    path(
        "friend_request/",
        FriendRequestView.as_view(),
        name="friend-request",
    ),
    path(
        "friend_request_response/",
        FriendRequestResponseView.as_view(),
        name="friend-request-response",
    ),
    path("friends/", FriendsListView.as_view(), name="friends-list"),
    path("pending_requests/", PendingRequestsView.as_view(), name="pending-requests"),
    path("user/search/", UserSearchView.as_view(), name="user-search"),
]
