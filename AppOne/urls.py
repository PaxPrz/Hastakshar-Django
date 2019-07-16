from django.urls import path
from AppOne import views


urlpatterns = [
    path('', views.index),
    path('index/', views.index),
    # path('index1/', views.index1),
    # path('login/', views.login, name = 'login'),
    # path('signup/', views.signup, name = 'signup'),
    path('register/', views.register, name = 'register'),
    path('user_login/', views.user_login, name = 'user_login'),
    path('upload/', views.upload, name = 'upload'),
    # path('upload_sign/', views.upload_sign, name='upload_sign'),
    path('train_sign/', views.train_sign, name='train_sign'),
    path('home/', views.home, name = 'home'),
    path('test_sign/', views.test_sign, name='test_sign'),
    path('uploadsign/', views.uploadsign, name = 'uploadsign'),
    path('welcome/', views.welcome, name='welc9ome'),

]



