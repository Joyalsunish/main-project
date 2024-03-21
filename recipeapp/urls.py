from django.contrib import admin
from django.urls import path,include
from .import views

urlpatterns = [
    path('',views.login,name='login'),
     path('register/',views.register,name='register'),
    path('index/',views.index,name='index'),
    path('logout/',views.logout, name='logout'),
    path('create/',views.create,name='create'),
    path('viewprofile/',views.viewprofile,name='viewprofile'),
    path('updateprofile/<int:id>/',views.updateprofile,name='updateprofile'),
    path('addrecipe/',views.addrecipe,name='addrecipe'),
    path('likes/<int:id>/',views.likes,name="likes"),
    path('home/',views.home,name="home"),
    path('viewotherprofile/<int:id>/',views.viewotherprofile,name='viewotherprofile'),
    path('delete/<int:id>/',views.deleterecipe,name='deleterecipe'),
    path('addcomment/<int:id>/',views.addcomment,name='addcomment'),
    path('follow/<int:id>/', views.follow, name='follow'),
    path('unfollow/<int:id>/', views.unfollow, name='unfollow'),
    path('prediction/',views.prediction,name='prediction'),
    path('view_profiel/',views.view_profiel,name='view_profiel'),
    path('message/',views.message,name='message'),
    path('send_message/',views.send_message,name='send_message'),
    path('load_content/<int:user_id>/',views.load_content,name='load_content'),
    path('save/<int:recipe_id>/',views.save,name='save'),
    path('savedrecipes/',views.savedrecipes,name='savedrecipes'),
]