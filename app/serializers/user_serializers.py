from rest_framework.serializers import ModelSerializer

from app.models.user import UserProductSearchPhrases, User


class UserProductSearchPhraseSerializer(ModelSerializer):
    class Meta:
        model = UserProductSearchPhrases
        fields = '__all__'


class UserSerializer(ModelSerializer):
    search_phrases = UserProductSearchPhraseSerializer(source='userproductsearchphrases_set', many=True)

    class Meta:
        model = User
        fields = '__all__'

