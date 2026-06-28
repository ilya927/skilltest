import json
import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.generic import TemplateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import (
    Test, TestResult, FriendRequest,
    Question, ChatMessage
)

from .services.ai_service import AIService


# =========================
# AI INIT
# =========================
ai = AIService()


# =========================
# SAFE JSON
# =========================
def safe_json(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", str(text), re.S)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
    return None


# =========================
# SUBJECT PAGES
# =========================
class MathPageView(TemplateView):
    template_name = "skillplatform/math.html"


class MathBattleView(TemplateView):
    template_name = "skillplatform/math_battle.html"


class PhysicsPageView(TemplateView):
    template_name = "skillplatform/physics.html"


class PhysicsBattleView(TemplateView):
    template_name = "skillplatform/physics_battle.html"


class ChemistryPageView(TemplateView):
    template_name = "skillplatform/chemistry.html"


class ChemistryBattleView(TemplateView):
    template_name = "skillplatform/chemistry_battle.html"


class BiologyPageView(TemplateView):
    template_name = "skillplatform/biology.html"


class BiologyBattleView(TemplateView):
    template_name = "skillplatform/biology_battle.html"


class EnglishPageView(TemplateView):
    template_name = "skillplatform/english.html"


class EnglishBattleView(TemplateView):
    template_name = "skillplatform/english_battle.html"


class HistoryPageView(TemplateView):
    template_name = "skillplatform/history.html"


class HistoryBattleView(TemplateView):
    template_name = "skillplatform/history_battle.html"


# =========================
# AI PAGE
# =========================
class AIPageView(TemplateView):
    template_name = "skillplatform/ai.html"


# =========================
# WELCOME
# =========================
class WelcomeView(TemplateView):
    template_name = "skillplatform/welcome.html"


# =========================
# GUEST LOGIN
# =========================
class GuestLoginView(View):
    def get(self, request):
        request.session["guest"] = True
        return redirect("home")


# =========================
# HOME
# =========================
class HomeView(View):
    def get(self, request):
        tests = Test.objects.filter(is_ai_generated=False)

        subjects = {
            "Mathematics": tests.filter(subject="math"),
            "Physics": tests.filter(subject="physics"),
            "Chemistry": tests.filter(subject="chemistry"),
            "Biology": tests.filter(subject="biology"),
            "English": tests.filter(subject="english"),
            "History": tests.filter(subject="history"),
        }

        return render(request, "skillplatform/home.html", {
            "subjects": subjects,
        })


# =========================
# AI CHAT
# =========================
@method_decorator(csrf_exempt, name="dispatch")
class AIChatView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get("message", "").strip()

            if not message:
                return JsonResponse({"response": "Empty message"}, status=400)

            response = ai.chat(message)

            if request.user.is_authenticated:
                ChatMessage.objects.create(
                    user=request.user,
                    message=message,
                    response=response
                )

            return JsonResponse({"response": response})

        except Exception as e:
            return JsonResponse({"response": str(e)}, status=500)


# =========================
# AI GENERATE TEST
# =========================
@method_decorator(csrf_exempt, name="dispatch")
class AIGenerateTestView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            text = data.get("text", "")
            subject = data.get("subject", "general")
            difficulty = data.get("difficulty", "medium")

            if not text:
                return JsonResponse({"error": "No text provided"}, status=400)

            raw = ai.generate_test(text, subject, difficulty)

            result = raw if isinstance(raw, dict) else safe_json(raw)

            if not result:
                result = {
                    "title": f"{subject} AI Test",
                    "questions": [
                        {
                            "text": "What is the main idea?",
                            "options": ["A", "B", "C", "D"],
                            "correct_index": 0
                        }
                    ]
                }

            test = Test.objects.create(
                title=result.get("title", "AI Test"),
                subject=subject,
                description=text[:200],
                is_ai_generated=True
            )

            for q in result["questions"]:
                options = q.get("options", ["A", "B", "C", "D"])

                Question.objects.create(
                    test=test,
                    text=q.get("text", "Question"),
                    option1=options[0],
                    option2=options[1],
                    option3=options[2],
                    option4=options[3],
                    correct_option=q.get("correct_index", 0) + 1
                )

            return JsonResponse({
                "success": True,
                "test_id": test.id,
                "redirect": f"/test/{test.id}/"
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# =========================
# TEST DETAIL
# =========================
class TestDetailView(LoginRequiredMixin, DetailView):
    model = Test
    template_name = "skillplatform/test_detail.html"
    context_object_name = "test"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["questions"] = self.object.questions.all()
        return context


# =========================
# SAVE RESULT
# =========================
class SaveResultView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            test = get_object_or_404(Test, id=pk)

            TestResult.objects.create(
                user=request.user,
                test=test,
                score=data.get("score", 0),
                total_questions=data.get("total_questions", 0),
                accuracy=data.get("accuracy", 0),
                duration=data.get("duration", 0),
                session_key=request.session.session_key or "no-session"
            )

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# =========================
# RESULTS
# =========================
class ResultsView(LoginRequiredMixin, View):
    def get(self, request):
        results = TestResult.objects.filter(user=request.user)
        return render(request, "skillplatform/results.html", {"results": results})


# =========================
# FRIENDS (FULL)
# =========================
class FriendsView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get("q", "").strip()

        sent = FriendRequest.objects.filter(from_user=request.user)
        received = FriendRequest.objects.filter(to_user=request.user)

        friends_from = FriendRequest.objects.filter(
            from_user=request.user,
            status="accepted"
        ).values_list("to_user", flat=True)

        friends_to = FriendRequest.objects.filter(
            to_user=request.user,
            status="accepted"
        ).values_list("from_user", flat=True)

        friends = User.objects.filter(id__in=list(friends_from) + list(friends_to))

        users = User.objects.none()

        if len(query) >= 2:
            users = User.objects.filter(
                username__istartswith=query
            ).exclude(id=request.user.id).exclude(
                id__in=friends.values_list("id", flat=True)
            )

        return render(request, "skillplatform/friends.html", {
            "users": users,
            "sent_requests": sent,
            "received_requests": received,
            "friends": friends,
            "query": query,
        })


class SendFriendRequestView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        to_user = get_object_or_404(User, id=user_id)

        if to_user != request.user:
            FriendRequest.objects.get_or_create(
                from_user=request.user,
                to_user=to_user,
                defaults={"status": "pending"}
            )

        return redirect("friends")


class AcceptFriendRequestView(LoginRequiredMixin, View):
    def get(self, request, request_id):
        fr = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
        fr.status = "accepted"
        fr.save()
        return redirect("friends")


class RejectFriendRequestView(LoginRequiredMixin, View):
    def get(self, request, request_id):
        fr = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
        fr.status = "rejected"
        fr.save()
        return redirect("friends")


# =========================
# FRIEND STATS
# =========================
class FriendStatView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        friend = get_object_or_404(User, id=user_id)

        is_friend = FriendRequest.objects.filter(status="accepted").filter(
            Q(from_user=request.user, to_user=friend) |
            Q(from_user=friend, to_user=request.user)
        ).exists()

        if not is_friend and friend != request.user:
            return redirect("friends")

        last_tests = TestResult.objects.filter(user=friend).order_by("-completed_at")[:5]
        avg_score = TestResult.objects.filter(user=friend).aggregate(avg=Avg("accuracy"))["avg"] or 0
        total_tests = TestResult.objects.filter(user=friend).count()

        return render(request, "skillplatform/friendstat.html", {
            "friend": friend,
            "last_tests": last_tests,
            "avg_score": avg_score,
            "total_tests": total_tests,
        })


# =========================
# COMPARE
# =========================
class CompareView(View):
    def get(self, request, user_id):
        friend = get_object_or_404(User, id=user_id)

        my_results = TestResult.objects.filter(user=request.user)
        friend_results = TestResult.objects.filter(user=friend)

        my_avg = my_results.aggregate(avg=Avg("accuracy"))["avg"] or 0
        friend_avg = friend_results.aggregate(avg=Avg("accuracy"))["avg"] or 0

        winner = "You" if my_avg > friend_avg else friend.username

        return render(request, "skillplatform/compare.html", {
            "friend": friend,
            "my_avg": my_avg,
            "friend_avg": friend_avg,
            "winner": winner,
        })


# =========================
# AUTH
# =========================
class RegisterView(View):
    def get(self, request):
        return render(request, "skillplatform/register.html")

    def post(self, request):
        username = request.POST.get("username")
        password1 = request.POST.get("password1")

        User.objects.create_user(username=username, password=password1)
        return redirect("login")


class LoginView(View):
    def get(self, request):
        return render(request, "skillplatform/login.html")

    def post(self, request):
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user:
            login(request, user)
            return redirect("home")

        return render(request, "skillplatform/login.html", {"error": "Invalid login"})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("welcome")


# =========================
# AITEST DATA (FIX FOR URL ERROR)
# =========================
class AITestDataView(View):
    def get(self, request, test_id):
        test = get_object_or_404(Test, id=test_id)

        questions = list(test.questions.values(
            "id", "text",
            "option1", "option2", "option3", "option4",
            "correct_option"
        ))

        return JsonResponse({
            "test_id": test.id,
            "title": test.title,
            "questions": questions
        })