from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Profile(models.Model):
   user=models.ForeignKey(User,on_delete=models.CASCADE)
   name=models.CharField(max_length=25)
   bio=models.TextField(blank=True)
   profileimg=models.ImageField(upload_to='profiles', default='blankproimg.webp')
   followers = models.ManyToManyField(User, related_name='followers', blank=True)
   following=models.ManyToManyField(User,related_name="following",blank=True)

   @property
   def imageURL(self):
        try:
            url = self.profileimg.url
        except:
            url = ''
        return  url
        
class Recipe(models.Model):
     user=models.ForeignKey(User,on_delete=models.CASCADE)
     profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
     recipeimg=models.ImageField(upload_to='recipes')
     name=models.CharField(max_length=25)
     ingredient=models.TextField()
     instruction=models.TextField()
     likes = models.ManyToManyField(Profile, related_name='liked_recipes')
     created_at=models.DateTimeField(auto_now_add=True)
     calorie=models.IntegerField()


     @property
     def imageURL(self):
      try:
         url = self.recipeimg.url
      except:
          url = ''
      return  url
     
class Comment(models.Model):
    recipe=models.ForeignKey(Recipe,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='shared_messages', on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class SavedRecipes(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    recipe=models.ForeignKey(Recipe,on_delete=models.CASCADE)