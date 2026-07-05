from django.urls import path

from .views import (
    WelcomeView,
    GuestLoginView,
    HomeView,

    TestDetailView,
    ResultsView,
    SaveResultView,

    RegisterView,
    LoginView,
    LogoutView,

    FriendsView,
    SendFriendRequestView,
    AcceptFriendRequestView,
    RejectFriendRequestView,
    FriendStatView,
    CompareView,

    MathPageView,
    MathBattleView,

    PhysicsPageView,
    PhysicsBattleView,

    ChemistryPageView,
    ChemistryBattleView,

    BiologyPageView,
    BiologyBattleView,

    EnglishPageView,
    EnglishBattleView,

    HistoryPageView,
    HistoryBattleView,

    # AI
    AIPageView,
    AIGenerateTestView,
    AIChatView,
    AITestDataView,

    TopWorldView, 
)

urlpatterns = [

    path("", WelcomeView.as_view(), name="welcome"),
    path("guest/", GuestLoginView.as_view(), name="guest_login"),
    path("home/", HomeView.as_view(), name="home"),

    # AI ROUTES
    path("ai/", AIPageView.as_view(), name="ai"),
    path("ai/chat/", AIChatView.as_view(), name="ai_chat"),
    path("ai/generate/", AIGenerateTestView.as_view(), name="ai_generate"),
    path("ai/test/<int:test_id>/data/", AITestDataView.as_view(), name="ai_test_data"),

    # TEST SYSTEM
    path("test/<int:pk>/", TestDetailView.as_view(), name="test_detail"),
    path("test/<int:pk>/save/", SaveResultView.as_view(), name="save_result"),
    path("results/", ResultsView.as_view(), name="results"),
    path("leaderboard/", TopWorldView.as_view(), name="leaderboard"),
    
    # FRIENDS
    path("friends/", FriendsView.as_view(), name="friends"),
    path("friends/send/<int:user_id>/", SendFriendRequestView.as_view(), name="send_friend"),
    path("friends/accept/<int:request_id>/", AcceptFriendRequestView.as_view(), name="accept_friend"),
    path("friends/reject/<int:request_id>/", RejectFriendRequestView.as_view(), name="reject_friend"),
    path("friend/<int:user_id>/", FriendStatView.as_view(), name="friendstat"),
    path("compare/<int:user_id>/", CompareView.as_view(), name="compare"),


    # SUBJECT PAGES
    path("math/", MathPageView.as_view(), name="math_page"),
    path("math-battle/", MathBattleView.as_view(), name="math_battle"),

    path("physics/", PhysicsPageView.as_view(), name="physics_page"),
    path("physics-battle/", PhysicsBattleView.as_view(), name="physics_battle"),

    path("chemistry/", ChemistryPageView.as_view(), name="chemistry_page"),
    path("chemistry-battle/", ChemistryBattleView.as_view(), name="chemistry_battle"),

    path("biology/", BiologyPageView.as_view(), name="biology_page"),
    path("biology-battle/", BiologyBattleView.as_view(), name="biology_battle"),

    path("english/", EnglishPageView.as_view(), name="english_page"),
    path("english-battle/", EnglishBattleView.as_view(), name="english_battle"),

    path("history/", HistoryPageView.as_view(), name="history_page"),
    path("history-battle/", HistoryBattleView.as_view(), name="history_battle"),


    # AUTH
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]