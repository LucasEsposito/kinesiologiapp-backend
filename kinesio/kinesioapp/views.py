from django.shortcuts import render
from django.views import generic
from users.models import SecretQuestion, Patient
from .models import ClinicalSession, Image
from django.http import HttpResponse
from django.contrib.auth import logout


class IndexView(generic.View):

    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            if user.is_medic:

                return render(request, 'kinesioapp/index.html', {'patients': user.related_patients})
            else:
                sessions = ClinicalSession.objects.accessible_by(user=user)
                return render(request, 'kinesioapp/index.html', {'sessions': sessions})
        else:
            return render(request, 'kinesioapp/index.html')


class SecretQuestionView(generic.View):
    def get(self, request):
        questions = SecretQuestion.objects.all()

        return render(request, 'kinesioapp/login/secret_question.html', {"questions": questions})


class NoUserView(generic.View):

    def get(self, request):
        return render(request, 'kinesioapp/login/no_user.html')


def logout_view(request):
    logout(request)
    return HttpResponse("User logout")


class ClinicalHistoryView(generic.View):
    def get(self, request):
        patient_id = request.GET.get("patient_id", None)
        patient = Patient.objects.get(pk=patient_id)
        sessions = ClinicalSession.objects.filter(patient_id=patient_id).order_by('-id')
        return render(request, 'kinesioapp/users/clinical_history.html',
                      {'sessions': sessions, 'patient': patient.user})


class ClinicalSessionView(generic.View):
    def get(self, request):
        clinical_session_id = request.GET.get("clinical_session_id", None)
        clinical_session = ClinicalSession.objects.get(pk=clinical_session_id)
        return render(request, 'kinesioapp/users/clinical_session.html', {'clinical_session': clinical_session})


class TimelapseView(generic.View):
    def get(self, request):
        tag = request.GET.get("tag", None)
        patient_id = request.GET.get("patient_id", None)
        images = Image.objects.filter(clinical_session__patient_id=patient_id, tag=tag)

        return render(request, 'kinesioapp/users/timelapse.html', {'images': images})
