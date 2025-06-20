from rest_framework import serializers
from .models import Circle, Contribution, Claim, Membership
from auths.serializers import RegisterSerializer
from .constants import FREQUENCY_CHOICES, MIN_FREQUENCY

class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = '__all__'
        read_only_fields = ['user', 'circle', 'is_automatic', 'timestamp', 'refunded']

class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = '__all__'
        read_only_fields = ['user', 'circle', 'status', 'processed_at', 'created_at']

class CircleSerializer(serializers.ModelSerializer):
    members = RegisterSerializer(many=True, read_only=True)
    contributions = ContributionSerializer(many=True, read_only=True)
    claims = ClaimSerializer(many=True, read_only=True)

    frequency = serializers.ChoiceField(
        choices=FREQUENCY_CHOICES,
        default=MIN_FREQUENCY,
        help_text="Contribution frequency (weekly/monthly)"
    )

    class Meta:
        model = Circle
        fields = '__all__'
        read_only_fields = ['creator', 'balance']

    def validate_frequency(self, value):
        if value not in dict(FREQUENCY_CHOICES):
            raise serializers.ValidationError("Invalid frequency option")
        return value

    def validate(self, data):
        if data.get('frequency') == 'daily' and not self.context.get('is_testing'):
            raise serializers.ValidationError(
                "Daily frequency is only allowed in testing"
            )
        return data

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'
        read_only_fields = ['join_date']
