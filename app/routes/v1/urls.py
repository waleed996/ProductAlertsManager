from rest_framework.routers import SimpleRouter

from app.controllers.user_controller import UserController


router = SimpleRouter(trailing_slash=False)
router.register('user', UserController, basename='user-crud')

urlpatterns = router.urls
