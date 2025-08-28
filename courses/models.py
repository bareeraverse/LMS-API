from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="courses_taught"
    )
    students = models.ManyToManyField(
        User, 
        related_name="enrolled_courses", 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(
        'Course',
        on_delete= models.CASCADE, related_name='modules'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Lesson(models.Model):
    module = models.ForeignKey(
        'Module', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['order', 'id']


    def __str__(self):
        return f"{self.module.title} · {self.title}"
    
class Quiz(models.Model):
    lesson = models.ForeignKey(
        'Lesson',
        on_delete= models.CASCADE,
        related_name='quizzes')
    title = models.CharField(max_length=200)
    description=models.TextField(blank=True)
    time_limit= models.IntegerField(help_text='Time limit in minutes', null=True, blank=True)

class Question(models.Model):
    quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.CharField(max_length=300)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200, blank=True, null=True)
    option_d = models.CharField(max_length=200, blank=True, null=True)

    CORRECT_CHOICES = [
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ]
    correct_option = models.CharField(max_length=1, choices=CORRECT_CHOICES)

    def __str__(self):
        return self.text

    
class QuixAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz=models.ForeignKey(
        'Quiz',
        on_delete=models.CASCADE,
        related_name='attempts')
    score=models.FloatField(default=0)
    completed_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user}-{self.quiz.title}-{self.score}'

class Answer(models.Model):
    attempt =  models.ForeignKey(
        QuixAttempt,
        on_delete=models.CASCADE,
        related_name='answers'
        )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_option = models.CharField(max_length=1, blank=True,null=True)
    def __str__(self):
        return f'{self.attempt.user}-{self.question.text}-{self.selected_option}'
    

class LessonProgress(models.Model):
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='lesson_progress')
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student}-{self.lesson}-{self.completed}"