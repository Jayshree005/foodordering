from django.contrib.auth import authenticate

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import User
from .models import ContactMessage
from .serializers import ContactMessageSerializer, ProfileSerializer, SignupSerializer


# =====================================
# USER LOGIN API
# =====================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):

    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user = authenticate(
        request,
        username=user_obj.username,
        password=password
    )

    if user is None:
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, created = Token.objects.get_or_create(
        user_id=user.pk
    )

    return Response(
        {
            'message': 'Login successful.',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone_number': user.phone_number,
                'user_type': user.user_type,
                'preferred_language': user.preferred_language,
                'delivery_address': user.delivery_address,
                'postal_code': user.postal_code
            }
        },
        status=status.HTTP_200_OK
    )


# =====================================
# USER SIGNUP API
# =====================================

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_user(request):

    serializer = SignupSerializer(data=request.data)

    if serializer.is_valid():

        user = serializer.save()

        token, created = Token.objects.get_or_create(
            user_id=user.pk
        )

        return Response(
            {
                'message': 'Account created successfully.',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'user_type': user.user_type,
                    'preferred_language': user.preferred_language,
                    'delivery_address': user.delivery_address,
                    'postal_code': user.postal_code
                }
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_contact_message(request):
    serializer = ContactMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(
        {'message': 'Your message has been received.'},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'PATCH':
        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(ProfileSerializer(request.user).data, status=status.HTTP_200_OK)