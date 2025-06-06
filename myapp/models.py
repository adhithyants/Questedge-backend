from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_detail')
    auth_user_id = models.IntegerField(null=True, blank=True) 
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avg_technical_score = models.FloatField(default=0)
    avg_aptitude_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)

    def __str__(self):
        return self.name

    def update_scores(self):
        attempts = self.attempts.all()
        if attempts:
            # Calculate averages
            self.avg_technical_score = attempts.aggregate(Avg('technical_marks'))['technical_marks__avg'] or 0
            self.avg_aptitude_score = attempts.aggregate(Avg('aptitude_marks'))['aptitude_marks__avg'] or 0
            # Calculate total score
            self.total_score = self.avg_technical_score + self.avg_aptitude_score
            self.save()

    def average_score(self):
        return round((self.avg_technical_score + self.avg_aptitude_score) / 2, 2) if (self.avg_technical_score + self.avg_aptitude_score) > 0 else 0

    class Meta:
        verbose_name = "User Detail"
        verbose_name_plural = "User Details"

class Attempt(models.Model):
    user = models.ForeignKey(UserDetail, related_name='attempts', on_delete=models.CASCADE)
    auth_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts_direct', null=True, blank=True)
    technical_marks = models.IntegerField(help_text="Technical marks")
    aptitude_marks = models.IntegerField(help_text="Aptitude marks")
    marks = models.IntegerField(help_text="Total marks (auto-calculated)", null=True, blank=True)
    attempt_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.marks = self.technical_marks + self.aptitude_marks
        super().save(*args, **kwargs)
        # Update user's average scores after saving attempt
        self.user.update_scores()

    def __str__(self):
        return f"{self.user} - Attempt on {self.attempt_date}"

    class Meta:
        verbose_name = "Attempt"
        verbose_name_plural = "Attempts"    
