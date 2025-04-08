from django.urls import path 
from .views import UserRegisterView, UserListView, UserRetrieveUpdateDestroyView, UserProfileView, LogoutView 
 
app_name="users" 
urlpatterns = [ 
    path('register/', UserRegisterView.as_view(), name='user-register'), 
    path('', UserListView.as_view(), name='user-list'), 
    path('<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), 
name='user-detail'), 
    path('profile/', UserProfileView.as_view(), name='user-profile'), 
    path('log-out/', LogoutView.as_view(), name='log-out'), 
]