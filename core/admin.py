from django.contrib import admin
from .models import Course, Module, Unit, Assessment, Question, Answer, UserProgress

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('course', 'order')

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'created_at')
    list_filter = ('module__course', 'module', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('module', 'order')

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'assessment_type', 'created_at')
    list_filter = ('assessment_type', 'unit__module__course', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'assessment', 'order')
    list_filter = ('assessment__assessment_type', 'assessment__unit__module__course')
    search_fields = ('question_text',)
    ordering = ('assessment', 'order')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__assessment__assessment_type')
    search_fields = ('answer_text',)

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'unit', 'completed', 'score', 'completed_at')
    list_filter = ('completed', 'unit__module__course', 'completed_at')
    search_fields = ('user__username', 'unit__title')
    ordering = ('-completed_at',)
