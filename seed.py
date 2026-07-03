import os
import django
import random
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skilltest.settings")
django.setup()

from django.contrib.auth.models import User
from skillplatform.models import Test, TestResult

users_data = [
    ("john_weak", "weak"),
    ("maria_slow", "weak"),
    ("sophia_easy", "weak"),
    ("alex_student", "normal"),
    ("david_brown", "normal"),
    ("emma_smart", "smart"),
    ("liam_pro", "smart"),
    ("noah_brain", "smart"),
    ("olivia_hardworker", "good"),
    ("michael_improving", "good"),
]

tests = list(Test.objects.all())

for username, level in users_data:
    user, created = User.objects.get_or_create(username=username)

    if created:
        user.set_password(username + "123")
        user.save()

    TestResult.objects.filter(user=user).delete()

    if level == "weak":
        test_count = random.randint(5, 8)
        min_p, max_p = 45, 65

    elif level == "normal":
        test_count = random.randint(8, 12)
        min_p, max_p = 60, 75

    elif level == "smart":
        test_count = random.randint(10, 15)
        min_p, max_p = 70, 85

    else:  # good (strong but not perfect)
        test_count = random.randint(12, 18)
        min_p, max_p = 75, 90

    for i in range(test_count):
        test = random.choice(tests)

        total = test.questions.count()

        score = max(1, int(total * random.uniform(min_p / 100, max_p / 100)))
        accuracy = (score / total) * 100 if total > 0 else 0

        TestResult.objects.create(
            user=user,
            test=test,
            score=score,
            total_questions=total,
            accuracy=accuracy,
            duration=random.randint(25, 200),
            session_key=f"{username}_{i}_{int(time.time())}"
        )

print("10 realistic users created (no perfect scores)")