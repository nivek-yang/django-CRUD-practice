from django.db import models

# Create your models here.
class Interview(models.Model):
    company_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    interview_at = models.DateField(null=True)
    rating = models.PositiveSmallIntegerField()
    review = models.TextField()
    result = models.CharField(max_length=100)

class Comment(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
