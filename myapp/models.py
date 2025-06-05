from django.db import models
from django.contrib.auth.models import User

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_detail')
    auth_user_id = models.IntegerField(null=True, blank=True) 
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def average_score(self):
        attempts = self.attempts.all()
        if not attempts:
            return 0
        total = sum((attempt.technical_marks + attempt.aptitude_marks) / 2 for attempt in attempts)
        return round(total / attempts.count(), 2)

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

    def __str__(self):
        return f"{self.user} - Attempt on {self.attempt_date}"

    class Meta:
        verbose_name = "Attempt"
        verbose_name_plural = "Attempts"    
