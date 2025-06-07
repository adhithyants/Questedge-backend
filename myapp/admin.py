from django.contrib import admin
from .models import UserDetail, Attempt

class AttemptInline(admin.TabularInline):
    model = Attempt
    extra = 1
    fields = ('technical_marks', 'aptitude_marks', 'attempt_date')
    readonly_fields = ('attempt_date',)

@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_email', 'avg_technical_score', 'avg_aptitude_score', 'total_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'user__email')
    ordering = ('-total_score',)
    fieldsets = (
        (None, {
            'fields': ('user', 'name')
        }),
        ('Scores', {
            'fields': ('avg_technical_score', 'avg_aptitude_score', 'total_score')
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'avg_technical_score', 'avg_aptitude_score', 'total_score')
    inlines = [AttemptInline]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'technical_marks', 'aptitude_marks', 'marks', 'attempt_date')
    list_filter = ('attempt_date',)
    search_fields = ('user__name', 'user__user__email')
    ordering = ('-attempt_date',)