from django.db import models
from django.contrib.auth.models import User

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_detail')
    auth_user_id = models.IntegerField(null=True, blank=True) 
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avg_technical_score = models.FloatField(default=0)  # Renamed to total_technical_score for clarity
    avg_aptitude_score = models.FloatField(default=0)  # Renamed to total_aptitude_score for clarity
    total_score = models.FloatField(default=0)

    def __str__(self):
        return self.name

    def update_scores(self):
        attempts = self.attempts.all()
        if attempts:
        # Sum all technical and aptitude marks
            self.avg_technical_score = sum(attempt.technical_marks for attempt in attempts) or 0
            self.avg_aptitude_score = sum(attempt.aptitude_marks for attempt in attempts) or 0
        # Calculate total score as the sum of technical and aptitude scores
            self.total_score = self.avg_technical_score + self.avg_aptitude_score
            self.save()

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
    category = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.marks = self.technical_marks + self.aptitude_marks
        super().save(*args, **kwargs)
        # Update user's total scores after saving attempt
        self.user.update_scores()

    def __str__(self):
        return f"{self.user} - Attempt on {self.attempt_date}"

    class Meta:
        verbose_name = "Attempt"
        verbose_name_plural = "Attempts"