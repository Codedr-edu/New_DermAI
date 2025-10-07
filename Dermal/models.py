from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    title = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Dermal_image(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    result = models.JSONField(blank=True, null=True)
    drug_history = models.TextField(blank=True, null=True)
    illness_history = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    heatmap = models.TextField(blank=True, null=True)
    more_predict = models.TextField(blank=True, null=True)
    symptom = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    # heatmap = models.TextField(blank=True, null=True)  # base64 string
    explain = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Image {self.id} uploaded at {self.uploaded_at}"


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = HTMLField()
    upvotes = models.ManyToManyField(
        Profile, related_name='upvoted_posts', blank=True)
    downvotes = models.ManyToManyField(
        Profile, related_name='downvoted_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = HTMLField()
    upvotes = models.ManyToManyField(
        Profile, related_name='upvoted_comments', blank=True)
    downvotes = models.ManyToManyField(
        Profile, related_name='downvoted_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.user.username} on {self.post.title}"
