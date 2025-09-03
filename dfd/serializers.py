from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# ---- Users ----
class UserSerializer(serializers.Serializer):
    key = serializers.CharField()
    email = serializers.EmailField()
    name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(required=False, allow_blank=True)
    meta = serializers.DictField(required=False)

# ---- Projects / Diagrams ----
class ProjectSerializer(serializers.Serializer):
    key = serializers.CharField()
    name = serializers.CharField()
    user_id = serializers.CharField(required=False, allow_blank=True)
    meta = serializers.DictField(required=False)
    owner_key = serializers.CharField(required=False, allow_blank=True)
    member_keys = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)

class DiagramSerializer(serializers.Serializer):
    key = serializers.CharField()
    name = serializers.CharField()
    meta = serializers.DictField(required=False)

# ---- Components (canvas schema) ----
VALID_TYPES = {"data_store", "external_entity", "process"}

class TypeEnumField(serializers.CharField):
    @extend_schema_field({
        "type": "string",
        "enum": ["data_store", "external_entity", "process", "external_entitiy"]  # include tolerated typo if you like
    })
    def to_representation(self, value):
        return super().to_representation(value)
    
class ComponentSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = TypeEnumField()
    position = serializers.DictField(child=serializers.FloatField(), allow_empty=False)
    size = serializers.DictField(child=serializers.FloatField(), allow_empty=False)
    data = serializers.DictField(allow_empty=False)

    def validate_type(self, value: str) -> str:
        v = value.strip().lower()
        if v == "external_entitiy":
            v = "external_entity"
        if v not in VALID_TYPES:
            raise serializers.ValidationError(f"type must be one of {sorted(VALID_TYPES)}")
        return v

    def validate_position(self, value):
        for k in ("x", "y"):
            if k not in value:
                raise serializers.ValidationError(f"position.{k} is required")
        return value

    def validate_size(self, value):
        for k in ("width", "height"):
            if k not in value:
                raise serializers.ValidationError(f"size.{k} is required")
        return value

    def validate_data(self, value):
        required = ["text", "color", "borderColor", "borderWidth", "textAlignment", "textSize"]
        missing = [k for k in required if k not in value]
        if missing:
            raise serializers.ValidationError(f"data missing fields: {missing}")
        return value
