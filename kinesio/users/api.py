from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from .models import CustomUser
from .serializers import CustomUserSerializer


class TokenGoogleAPIView(APIView):
    def post(self, request):
        google_token = request.data.get('google_token', None)
        if google_token is None:
            return Response({'error': 'Missing token'}, status=status.HTTP_404_NOT_FOUND)
        else:
            print(google_token)
            try:
                id_info = id_token.verify_oauth2_token(
                    google_token,
                    requests.Request(),
                    '1093191472549-9gk2os2g3hm2qa1bhrhr1ab0cl7r5qkb.apps.googleusercontent.com')

                if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    return Response({'error': 'Invalid Issuer'}, status=status.HTTP_404_NOT_FOUND)

                user_id = id_info['sub']

                query_user = CustomUser.objects.filter(id_google=user_id)
                if query_user.count() > 0:
                    return Response({'warning': 'User do not exist.'}, status=status.HTTP_206_PARTIAL_CONTENT)
                else:
                    # FIXME Cambiar para que devuelva las preguntas cuando el ISSUE 94 este terminado
                    return Response({'questions': 'Saraza!'}, status=status.HTTP_200_OK)
            except ValueError:
                return Response({'error': 'Invalid Token. Please verify'}, status=status.HTTP_404_NOT_FOUND)


class PatientsAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.patients()
    serializer_class = CustomUserSerializer


class PatientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.patients()
    serializer_class = CustomUserSerializer


class MedicsAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.medics()
    serializer_class = CustomUserSerializer
