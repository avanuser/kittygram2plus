from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Achievement, Cat, User

from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .permissions import OwnerOrReadOnly, ReadOnly
from .throttling import WorkingHoursRateThrottle
from .pagination import CatsPagination


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = (OwnerOrReadOnly,)
    # throttle_classes = (AnonRateThrottle,) # Подключим класс AnonRateThrottle
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # А далее применится лимит low_request
    throttle_scope = 'low_request'
    # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    pagination_class = CatsPagination
    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year')
    search_fields = ('name',)    # пример поискового запроса: /cats/?search=mur
    # пример поика по полям связанных моделей:
    search_fields = ('achievements__name', 'owner__username')
    # пример, значение параметра search должно быть началом искомой строки:
    search_fields = ('^name',)
    ordering_fields = ('name', 'birth_year')    # поля для сортировки
    ordering = ('birth_year',)    # поля для сортировки по умолчанию

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернём обновлённый перечень используемых пермишенов
            return (ReadOnly(),)
        # Для ост-х ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
