from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True,default='profile_pictures/profile.jpg')
    phn_number = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)  
    country = models.CharField(max_length=100, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    is_signup_user = models.BooleanField(default=False) 

    def __str__(self):
        # Safely access the username or return a fallback value
        return self.user.username if self.user else "No username"

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    goalAmount = models.FloatField()
    collectedAmount = models.FloatField(default=0.0)
    createdAt = models.DateTimeField(auto_now_add=True)
    startDate = models.DateField()
    endDate = models.DateField()
    image = models.ImageField(upload_to='projects/', default='projects/default.jpg')
    profile = models.ForeignKey(Profile, related_name='projects', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status_choices = (
        ('OnGoing', 'On Going'),
        ('Coming Soon', 'Coming Soon'),
        ('Completed', 'Completed'),  # Added an additional status for completion
    )
    status = models.CharField(max_length=50, choices=status_choices, default='OnGoing')

    def __str__(self):
        return self.title

    
class Donation(models.Model):
    profile = models.ForeignKey(Profile, related_name='donations', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, related_name='donations', on_delete=models.CASCADE, null=True, blank=True)  # Optional link to projects
    def __str__(self):
        return f"Donation of ${self.amount} on {self.created_at}"


class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    stars = models.IntegerField()
    ratingDate = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Rating of {self.stars} stars for {self.project.title}"


class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    content = models.TextField()
    commentDate = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.project.title} - {self.content[:30]}"


class Report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reportReason = models.TextField()
    reportDate = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.project.title} - {self.reportReason[:30]}"



class FeatureProject(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    goalAmount = models.FloatField(default=0.0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)  # Optional association
    createdAt = models.DateField(auto_now_add=True, blank=True, null=True)
    startDate = models.DateField(blank=True, null=True)
    endDate = models.DateField(blank=True, null=True)

    select_choice = (
        ('OnGoing', 'OnGoing'),
        ('Coming Soon', 'Coming Soon'),
    )
    status = models.CharField(max_length=50, choices=select_choice)

    def __str__(self):
        return self.title

