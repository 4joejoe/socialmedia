from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.shortcuts import render
from django.views.decorators.cache import cache_page

# from drf_yasg import openapi
# from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

# Create your views here.
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q

from authapp.serializers import UserSerializer

from .models import CustomUser

# Create your views here.


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [AllowAny]
        return super(UserView, self).get_permissions()

    def post(self, request: Request) -> Response:
        # self.permission_classes = [AllowAny]

        serialized_data = UserSerializer(
            data=request.data, context={"request": request}
        )
        if serialized_data.is_valid():
            serialized_data.save()
            return Response(serialized_data.data, status=201)
        return Response(serialized_data.errors, status=400)

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=200)
        else:
            return Response("User not authenticated", status=401)

    # create user update and logout and delete views
    def put(self, request, *args, **kwargs):
        if "user_id" in kwargs:
            try:
                user = CustomUser.objects.get(id=kwargs["user_id"])
                serializer = UserSerializer(user, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=200)
                return Response(serializer.errors, status=400)
            except CustomUser.DoesNotExist:
                return Response("User not found", status=404)
        return Response("User ID is required", status=400)

    def delete(self, request, *args, **kwargs):
        if "user_id" in kwargs:
            try:
                user = CustomUser.objects.get(id=kwargs["user_id"])
                user.delete()
                return Response("User deleted successfully", status=200)
            except CustomUser.DoesNotExist:
                return Response("User not found", status=404)
        return Response("User ID is required", status=400)

    def logout(self, request, *args, **kwargs):
        if "user_id" in kwargs:
            try:
                user = CustomUser.objects.get(id=kwargs["user_id"])
                user.delete()
                return Response("User logged out successfully", status=200)
            except CustomUser.DoesNotExist:
                return Response("User not found", status=404)
        return Response("User ID is required", status=400)


class FriendRequestThrottle(UserRateThrottle):
    rate = "3/min"


class FriendRequestView(APIView):
    throttle_classes = [FriendRequestThrottle]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get("to_user_id")
        if not to_user_id:
            return Response("User ID is required", status=status.HTTP_400_BAD_REQUEST)

        try:
            to_user = CustomUser.objects.get(id=to_user_id)
        except CustomUser.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        # # Limit friend requests to 3 per minute
        # one_minute_ago = timezone.now() - timedelta(minutes=1)
        # recent_requests = FriendRequest.objects.filter(
        #     from_user=request.user, timestamp__gte=one_minute_ago
        # )
        # if recent_requests.count() >= 3:
        #     return Response(
        #         "Too many requests. Please wait a moment and try again.",
        #         status=status.HTTP_429_TOO_MANY_REQUESTS,
        #     )

        request.user.send_friend_request(to_user)
        return Response("Friend request sent", status=status.HTTP_200_OK)


class FriendRequestResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from_user_id = request.data.get("from_user_id")
        action = request.data.get("action")  # 'accept' or 'reject'

        if not from_user_id or not action:
            return Response(
                "Both user ID and action are required",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from_user = CustomUser.objects.get(id=from_user_id)
        except CustomUser.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        if action == "accept":
            request.user.accept_friend_request(from_user)
            return Response("Friend request accepted", status=status.HTTP_200_OK)
        elif action == "reject":
            request.user.reject_friend_request(from_user)
            return Response("Friend request rejected", status=status.HTTP_200_OK)
        else:
            return Response("Invalid action", status=status.HTTP_400_BAD_REQUEST)


class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        friends = request.user.friends.all()
        friends_data = [
            {"id": friend.id, "username": friend.username} for friend in friends
        ]
        return Response(friends_data, status=status.HTTP_200_OK)


class PendingRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pending_requests = request.user.pending_friend_requests()
        pending_requests_data = [
            {"id": req.from_user.id, "username": req.from_user.username}
            for req in pending_requests
        ]
        return Response(pending_requests_data, status=status.HTTP_200_OK)


class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        search_keyword = request.query_params.get("keyword", "")
        page_number = request.query_params.get("page", 1)

        # If search keyword matches exact email then return user associated with the email.
        try:
            user = CustomUser.objects.get(email=search_keyword)
            return Response(
                {"id": user.id, "username": user.username, "email": user.email},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            pass

        # If the search keyword contains any part of the name then return a list of all users.
        users = CustomUser.objects.filter(
            Q(first_name__icontains=search_keyword)
            | Q(last_name__icontains=search_keyword)
        )
        paginator = Paginator(users, 10)  # Show 10 users per page.
        page = paginator.get_page(page_number)

        users_data = [
            {"id": user.id, "username": user.username, "email": user.email}
            for user in page
        ]
        return Response(users_data, status=status.HTTP_200_OK)
