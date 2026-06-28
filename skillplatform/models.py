from django.db import models
from django.contrib.auth.models import User


# =========================
# 📚 TEST
# =========================
class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=50, default="math")
    is_ai_generated = models.BooleanField(default=False)
    def __str__(self):
        return self.title


# =========================
# ❓ QUESTION
# =========================
class Question(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    text = models.CharField(max_length=255)

    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)

    correct_option = models.IntegerField()

    def __str__(self):
        return self.text


# =========================
# 📊 TEST RESULT
# =========================
class TestResult(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="results"
    )

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="results"
    )

    score = models.IntegerField()
    total_questions = models.IntegerField()
    accuracy = models.FloatField()
    duration = models.IntegerField()  

    session_key = models.CharField(max_length=100)

    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]

    @property
    def formatted_duration(self):
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.accuracy}%"


# =========================
# 👥 FRIEND REQUEST SYSTEM
# =========================
class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_requests"
    )

    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_requests"
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"


# =========================
# 🧠 FRIENDS HELPER FUNCTION
# =========================
def get_friends(user):
    sent = FriendRequest.objects.filter(
        from_user=user,
        status="accepted"
    ).values_list("to_user", flat=True)

    received = FriendRequest.objects.filter(
        to_user=user,
        status="accepted"
    ).values_list("from_user", flat=True)

    return User.objects.filter(id__in=list(sent) + list(received))


# =========================
# 🤖 AI GENERATION LOG
# =========================
class AIGeneration(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_generations",
        null=True,
        blank=True
    )

    source_text = models.TextField()

    subject = models.CharField(max_length=50, default="general")

    difficulty = models.CharField(
        max_length=10,
        choices=[
            ("easy", "Easy"),
            ("medium", "Medium"),
            ("hard", "Hard"),
        ],
        default="medium"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Test ({self.subject} - {self.difficulty})"


# =========================
# 💬 AI CHAT MESSAGES
# =========================
class ChatMessage(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages"
    )

    message = models.TextField()
    response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}"