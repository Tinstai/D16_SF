from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', Profile.as_view(), name='profile'),
    path('feedbacks/', consideration, name='consideration'),
    path('', PublishBoard.as_view(), name='board', ),
    path('post/', PublishPost.as_view(), name='post', ),
    path('<int:pk>/', PublishDetail.as_view(), name='detail', ),
    path('<int:pk>/update/', PublishUpdate.as_view(), name='update', ),
    path('<int:pk>/delete/', PublishDelete.as_view(), name='delete'),
]
