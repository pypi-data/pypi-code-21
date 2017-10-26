# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from .viewsets import (
    SurveyViewSet,
    SectionViewSet,
    QuestionViewSet,
    SurveyedObjectViewSet,
    AnswerViewSet,
    OtherAnswerViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r'surveys', SurveyViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'surveyeds', SurveyedObjectViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'other-answers', OtherAnswerViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
]
