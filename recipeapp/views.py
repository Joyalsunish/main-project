
import io
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Profile,Recipe,Comment,Message,SavedRecipes
from django.contrib import messages,auth
from .form import ProfileForm
from .formrecipe import RecipeForm
from django.shortcuts import get_object_or_404, render,redirect
from django.http import JsonResponse
import tensorflow as tf
import numpy as np
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
import base64

from recipeapp import models


# Create your views here.

def index(request):
    return render(request,'index.html')

def register(request):
    if request.method=='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        uname=request.POST['username']
        password=request.POST['password']
        cpass=request.POST['cpass']
        if password==cpass:
            if User.objects.filter(username=uname).exists():
                messages.info(request,"username already taken")
            elif User.objects.filter(email=email).exists():
                messages.info(request,"email already taken")
            else:
                user=User.objects.create_user(first_name=fname,last_name=lname,email=email,username=uname,password=password)
                user.save()
                return render(request,'login.html')
        else:
            messages.info(request,"password not matching")
    return render(request,'register.html')

def login(request):
    if request.method=='POST':
        uname=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(username=uname,password=password)
        if user is not None:
            auth.login(request,user)
            if request.user.is_authenticated:
                user_id = request.user.id
                try:
                    profile=Profile.objects.get(user_id=user_id)
                    recipes = Recipe.objects.filter(user=request.user)
                    followers_count = profile.followers.count()
                    following_count = profile.following.count()

                    return render(request,'viewprofile.html',{'profile':profile,'recipes':recipes,'followers_count':followers_count,'following_count':following_count})
                except:
                    return render(request,'createprofile.html')
            else:
                messages.info(request,"invalid entry")
    return render(request,'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def create(request):
    if request.method=='POST':
        if request.user.is_authenticated:
            user_id = request.user.id
            img=request.FILES['img']
            name=request.POST['name']
            bio=request.POST['bio']
            profile=Profile(user_id=user_id,profileimg=img,name=name,bio=bio)
            profile.save()
            return render(request,'viewprofile.html',{'profile':profile})
    return render(request,'createprofile.html')

def viewprofile(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        profile=Profile.objects.get(user_id=user_id)
        recipes = Recipe.objects.filter(user=request.user)
        followers_count = profile.followers.count()
        following_count = profile.following.count()
        followers_list=profile.followers.all()
        following_list=profile.following.all()
        return render(request,'viewprofile.html',{'profile':profile,'recipes':recipes,'followers_count':followers_count,'following_count':following_count,'followers_list': followers_list,'following_list': following_list})
    
def updateprofile(request, id):
    profile = Profile.objects.get(user_id=id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('viewprofile')

    else:
        form = ProfileForm(instance=profile)
    return render(request, 'updateprofile.html', {'form': form, 'profile': profile})

 
def addrecipe(request):
    if request.method=='POST':
        if request.user.is_authenticated:
            user=request.user
            user_id=request.user.id
            profile=Profile.objects.get(user_id=user_id)
            profile_id=profile.id
            recipeimg=request.FILES['recipeimg']
            name=request.POST['name']
            ingredients=request.POST['ingredients']
            instructions=request.POST['instructions']
            calorie=request.POST['calorie']
            recipe=Recipe(user=user,profile_id=profile_id,recipeimg=recipeimg,name=name,ingredient=ingredients,instruction=instructions,calorie=calorie)
            recipe.save()
            return redirect('viewprofile')
            # return render(request,'viewprofile.html')
    return render(request,'addrecipe.html')


# def likes(request,id):
#     recipe=Recipe.objects.get(id=id)
#     recipe.likes+=1
#     recipe.save()
#     return redirect('viewprofile')

# def likes(request, id):
#     recipe = Recipe.objects.get(id=id)
#     profile = Profile.objects.get(user=request.user)
#     if recipe.user == request.user or recipe.profile == profile or profile.id in [user.id for user in recipe.likes.all()]:
#         return redirect('viewprofile')
#     recipe.likes += 1
#     recipe.save()
#     return redirect('viewprofile')

# def likes(request, id):
#     recipe = Recipe.objects.get(id=id)
#     profile = Profile.objects.get(user=request.user)
#     if recipe.user == request.user or recipe.profile == profile or profile.id in [user.id for user in recipe.likes.all()]:
#        return redirect('viewprofile')
#     recipe.likes += 1
#     recipe.save()
#     likes_count = recipe.likes.count()
#     return JsonResponse({'likes_count': likes_count})


def likes(request, id):
    recipe = Recipe.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    if profile in recipe.likes.all():
        recipe.likes.remove(profile)  # Remove like if already liked
        action = 'disliked'
    else:
        recipe.likes.add(profile)  # Add like if not liked
        action = 'liked'
    likes_count = recipe.likes.count()
    return JsonResponse({'action': action, 'likes_count': likes_count})



def home(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    following = profile.following.all()

    if request.method == 'POST':
        search_query = request.POST.get('search', '')

        try:
            calorie_search = int(search_query)
            recipes = Recipe.objects.filter(calorie=calorie_search)
        except ValueError:
            recipes = Recipe.objects.filter(Q(user__in=following) & (Q(name__icontains=search_query) | Q(ingredient__icontains=search_query)))

        return render(request, 'home.html', {'recipes': recipes, 'following': following,'profile':profile})

    else:
        recipes = Recipe.objects.filter(user__in=following).order_by('-created_at')
        otheruser = User.objects.exclude(id__in=following)
        return render(request, 'home.html', {'recipes': recipes, 'otheruser': otheruser, 'following': following})


def viewotherprofile(request,id):
    user=User.objects.get(id=id)
    profile=Profile.objects.get(user=user)
    recipes = Recipe.objects.filter(user=user)
    followers_count = profile.followers.count()
    following_count = profile.following.count()
    followers=profile.followers.all()
    following=profile.following.all()
    return render(request,'viewotherprofile.html',{'user':user,'profile':profile,'recipes':recipes,'followers_count':followers_count,'following_count':following_count,'followers':followers,'following':following})

def deleterecipe(request,id):
    recipe=Recipe.objects.get(id=id)
    recipe.delete()
    return redirect('viewprofile')

def addcomment(request, id):
    if request.user.is_authenticated:
        user_id = request.user.id
        recipe = Recipe.objects.get(id=id)
        recipe_id=recipe.id
        if request.method == 'POST':
            c = request.POST['comment']
            comment = Comment(user_id=user_id, recipe_id=recipe_id, content=c)
            comment.save()
            return redirect('home') 
    comments = Comment.objects.filter(recipe=recipe)
    return render(request, 'home.html',{'comments':comments})


def displaycomments(request,id):
    recipe = Recipe.objects.get(id=id)
    comments = Comment.objects.filter(recipe=recipe)
    return redirect('home',{'comments':comments})

# def follow(request, username):
#     user_to_follow = User.objects.get(username=username)
#     profile_to_follow = Profile.objects.get(user=user_to_follow)
#     current_user_profile = Profile.objects.get(user=request.user)
#     if profile_to_follow != current_user_profile:
#         current_user_profile.followers.add(user_to_follow)
#         return redirect('viewotherprofile', id=user_to_follow.id)
#     else:
#         return redirect('viewotherprofile', id=user_to_follow.id)

# def unfollow(request, id):
#     user_to_unfollow = User.objects.get(id=id)
#     current_user_profile = Profile.objects.get(user=request.user)
#     current_user_profile.followers.remove(user_to_unfollow)
#     context = {'current_user_profile': current_user_profile, 'id': user_to_unfollow.id}
#     return redirect('viewotherprofile',context=context)

def follow(request, id):
    if request.user.is_authenticated:
        user_to_follow = get_object_or_404(User, id=id)
        profile_to_follow = Profile.objects.get(user=user_to_follow)
        current_user_profile = Profile.objects.get(user=request.user)

        if profile_to_follow != current_user_profile:
            current_user_profile.following.add(profile_to_follow.user)
            profile_to_follow.followers.add(request.user)
            
        return redirect('viewotherprofile', id=id)
    
def unfollow(request, id):
    if request.user.is_authenticated:
        user_to_unfollow = get_object_or_404(User, id=id)
        profile_to_unfollow = Profile.objects.get(user=user_to_unfollow)
        current_user_profile = Profile.objects.get(user=request.user)

        if profile_to_unfollow != current_user_profile:
            current_user_profile.following.remove(profile_to_unfollow.user)
            profile_to_unfollow.followers.remove(request.user)
            
        return redirect('viewotherprofile', id=id)
    
 
    

def prediction(request):
    if request.method == 'POST':
        img = request.FILES['preimg']
        model = tf.keras.models.load_model(r"C:\Users\JOYAL SUNISH\Downloads\recipe_project\recipeinsocialmedia\recipe\trained_model.h5")

            # Process the uploaded image
        img_bytes = img.read()
        img_stream = io.BytesIO(img_bytes)
        image = tf.keras.preprocessing.image.load_img(img_stream, target_size=(64, 64))
        input_arr = tf.keras.preprocessing.image.img_to_array(image)
        input_arr = np.array([input_arr])
        predictions = model.predict(input_arr)
            
            # Check the shape of predictions
        if predictions.shape[-1] == 1:
            result_index = int(np.round(predictions[0][0]))
        else:
            result_index = np.argmax(predictions[0])

            # Load class names from labels.txt
        with open(r'C:\Users\JOYAL SUNISH\Downloads\recipe_project\recipeinsocialmedia\recipe\labels.txt', 'r') as f:
            class_names = [line.strip() for line in f]

            # Check if the result_index is within the valid range
        if 0 <= result_index < len(class_names):
            predicted_class = class_names[result_index]
            recipes=Recipe.objects.filter(ingredient__icontains=predicted_class)
                # Save the uploaded image to the media directory
            file_name = default_storage.save('uploaded_image.jpg', ContentFile(img_bytes))
            file_url = default_storage.url(file_name)
           

                # Render the result in the template
            return render(request, 'prediction.html', {'predicted_class': predicted_class, 'image_url': file_url,'recipes':recipes})
        else:
            print('Invalid predicted class index.')
            return render(request, 'prediction.html', {'predicted_class': 'Unknown'})

    return render(request, 'prediction.html')
    
def view_profiel(request):
    return render(request,'view_pro.html')

def message(request):
    users=User.objects.all()
    messages = Message.objects.filter(recipient=request.user)
    return render(request, 'message.html', {'messages': messages,'users':users})

def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        content = request.POST.get('content')
        recipe_id = request.POST.get('recipe_id')

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            messages.error(request, 'Invalid recipient.')
            return redirect('message')

        recipe = None
        if recipe_id:
            try:
                recipe = Recipe.objects.get(id=recipe_id)
            except Recipe.DoesNotExist:
                messages.error(request, 'Invalid recipe.')
                return redirect('message')

        message = Message.objects.create(sender=request.user, recipient=recipient, recipe=recipe, content=content)
        message.save()
        if recipe:
            return redirect('home')  # Redirect to home.html for recipe image
        else:
            return redirect('load_content', user_id=recipient_id)
    return redirect('message')

def load_content(request,user_id):
    user = request.user
    other_user = User.objects.get(id=user_id)
    messages = Message.objects.filter(
        (Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user))
    ).order_by('timestamp')

    context = {
        'messages': messages,
        'other_user': other_user,
        'users': User.objects.all()
    }
    return render(request,'message.html',context)

def save(request,recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if not SavedRecipes.objects.filter(user=request.user, recipe=recipe).exists():
        saved_recipe = SavedRecipes(user=request.user, recipe=recipe)
        saved_recipe.save()
    return redirect('home')

def savedrecipes(request):
    saved_recipes = SavedRecipes.objects.filter(user=request.user)
    return render(request, 'savedrecipes.html', {'saved_recipes': saved_recipes})