import os
import django
import random
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skilltest.settings")
django.setup()

from django.contrib.auth.models import User
from skillplatform.models import Test, TestResult

new_users = [
    ("jake_wilson", "weak"),
    ("lucas_gray", "weak"),
    ("nina_cooper", "normal"),
    ("ethan_clark", "normal"),
    ("sara_jones", "smart"),
    ("ben_smith", "smart"),
    ("lily_adams", "good"),
    ("ryan_moore", "good"),
    ("mia_taylor", "normal"),
    ("dylan_scott", "smart"),
]

tests = list(Test.objects.all())

for username, level in new_users:
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

    else:  # good
        test_count = random.randint(12, 18)
        min_p, max_p = 75, 90

    for i in range(test_count):
        test = random.choice(tests)

        total = test.questions.count()

        base = random.uniform(min_p, max_p)
        noise = random.uniform(-6, 6)

        final_accuracy = max(40, min(95, base + noise + random.random()))

        score = max(1, int(total * final_accuracy / 100))

        accuracy = round(
            (score / total) * 100 + random.uniform(-0.9, 0.9),
            2
        )

        accuracy = max(40, min(95, accuracy))

        TestResult.objects.create(
            user=user,
            test=test,
            score=score,
            total_questions=total,
            accuracy=accuracy,
            duration=random.randint(25, 200),
            session_key=f"{username}_{i}_{int(time.time())}"
        )

print("DONE: 10 new users created with realistic unique stats")