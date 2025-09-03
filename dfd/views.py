from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Project, Diagram, DFDNode, Process, ExternalEntity, DataStore, UserNode
from .serializers import ProjectSerializer, DiagramSerializer, ComponentSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample
from .serializers import ProjectSerializer, DiagramSerializer, ComponentSerializer, UserSerializer


TYPE_TO_NODE = {
    "process": Process,
    "external_entity": ExternalEntity,
    "data_store": DataStore,
}

def serialize_project(p: Project):
    # owner (0..1)
    owner = None
    owners = p.owner.all()
    if owners:
        o = owners[0]
        owner = {"key": o.key, "email": o.email, "name": o.name, "role": o.role}

    # members (0..N)
    members = [
        {"key": m.key, "email": m.email, "name": m.name, "role": m.role}
        for m in p.members.all()
    ]

    return {
        "key": p.key,
        "name": p.name,
        "user_id": p.user_id,
        "meta": p.meta,
        "owner": owner,
        "members": members,
    }
    

def get_project_or_404(project_id):
    proj = Project.nodes.first_or_none(key=project_id)
    if not proj:
        raise Http404("Project not found")
    return proj

def get_diagram_or_404(diagram_id):
    dia = Diagram.nodes.first_or_none(key=diagram_id)
    if not dia:
        raise Http404("Diagram not found")
    return dia

def ensure_diagram_in_project(proj, dia):
    if not proj.diagrams.is_connected(dia):
        raise Http404("Diagram not found in project")

def type_of_node(node):
    if isinstance(node, Process):
        return "process"
    if isinstance(node, ExternalEntity):
        return "external_entity"
    if isinstance(node, DataStore):
        return "data_store"
    return "unknown"

def serialize_component(node):
    return {
        "id": node.key,
        "type": type_of_node(node),
        "position": {"x": node.pos_x, "y": node.pos_y},
        "size": {"width": node.width, "height": node.height},
        "data": node.ui or {
            "text": node.name,
            "color": 4294967295,
            "borderColor": 4278190080,
            "borderWidth": 2,
            "textAlignment": "center",
            "textSize": 20
        }
    }
    
@extend_schema(
    tags=["Users"],
    request=UserSerializer,
    responses={201: UserSerializer, 200: UserSerializer},
    examples=[
        OpenApiExample(
            "Create user",
            value={"key": "user_bassiman", "email": "bassi@example.com", "name": "Bassiman", "role": "owner"},
            request_only=True
        )
    ]
)
class UserListCreateView(APIView):
    """
    GET  /api/users/
    POST /api/users/
    """
    def get(self, request):
        users = UserNode.nodes.all()
        data = [
            {"key": u.key, "email": u.email, "name": u.name, "role": u.role, "meta": u.meta}
            for u in users
        ]
        return Response(data)

    def post(self, request):
        s = UserSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        user = UserNode.nodes.first_or_none(key=d["key"])
        if not user:
            user = UserNode(**d).save()
        else:
            user.email = d.get("email", user.email)
            user.name = d.get("name", user.name)
            user.role = d.get("role", user.role)
            user.meta = d.get("meta", user.meta or {})
            user.save()

        return Response(
            {"key": user.key, "email": user.email, "name": user.name, "role": user.role, "meta": user.meta},
            status=status.HTTP_201_CREATED
        )
@extend_schema(
    tags=["Users"],
    parameters=[OpenApiParameter("user_key", OpenApiTypes.STR, OpenApiParameter.PATH)],
    responses={200: UserSerializer, 404: None}
)
class UserDetailView(APIView):
    """
    GET    /api/users/<user_key>/
    PATCH  /api/users/<user_key>/
    DELETE /api/users/<user_key>/
    """
    def get(self, request, user_key):
        user = UserNode.nodes.first_or_none(key=user_key)
        if not user:
            raise Http404("User not found")
        return Response({"key": user.key, "email": user.email, "name": user.name, "role": user.role, "meta": user.meta})

    def patch(self, request, user_key):
        user = UserNode.nodes.first_or_none(key=user_key)
        if not user:
            raise Http404("User not found")

        s = UserSerializer(data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        if "email" in d: user.email = d["email"]
        if "name" in d: user.name = d["name"]
        if "role" in d: user.role = d["role"]
        if "meta" in d: user.meta = d["meta"]
        user.save()

        return Response({"key": user.key, "email": user.email, "name": user.name, "role": user.role, "meta": user.meta})

    def delete(self, request, user_key):
        user = UserNode.nodes.first_or_none(key=user_key)
        if not user:
            raise Http404("User not found")

        # Optional: detach from projects before delete
        for p in user.owns:         # projects owned by this user
            p.owner.disconnect(user)
        for p in user.memberships:  # projects where member
            p.members.disconnect(user)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ------------------------
# Projects
# ------------------------

@extend_schema(
    tags=["Projects"],
    request=ProjectSerializer,
    responses={200: ProjectSerializer, 201: ProjectSerializer}
)
class ProjectListCreateView(APIView):
    def get(self, request):
        projects = Project.nodes.all()
        data = [serialize_project(p) for p in projects]
        return Response(data)

    def post(self, request):
        s = ProjectSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        proj = Project.nodes.first_or_none(key=d["key"]) or Project(**d)
        proj.name = d["name"]
        proj.user_id = d.get("user_id")
        proj.meta = d.get("meta", proj.meta or {})
        proj.save()

        # owner/members (optional) by keys
        owner_key = d.get("owner_key")
        if owner_key:
            user = UserNode.nodes.first_or_none(key=owner_key)
            if not user:
                return Response({"error": f"owner_key '{owner_key}' not found"}, status=400)
            # ensure single owner: disconnect previous owners
            for prev in proj.owner:
                proj.owner.disconnect(prev)
            proj.owner.connect(user)

        member_keys = d.get("member_keys") or []
        for mk in member_keys:
            mu = UserNode.nodes.first_or_none(key=mk)
            if not mu:
                return Response({"error": f"member_key '{mk}' not found"}, status=400)
            if not proj.members.is_connected(mu):
                proj.members.connect(mu)

        return Response(serialize_project(proj), status=status.HTTP_201_CREATED)

@extend_schema(
    tags=["Projects"],
    parameters=[OpenApiParameter("project_id", OpenApiTypes.STR, OpenApiParameter.PATH)],
    responses={200: ProjectSerializer, 404: None}
)
class ProjectDetailView(APIView):
    def get(self, request, project_id):
        proj = get_project_or_404(project_id)
        return Response(serialize_project(proj))

    def patch(self, request, project_id):
        proj = get_project_or_404(project_id)
        s = ProjectSerializer(data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        if "name" in d: proj.name = d["name"]
        if "user_id" in d: proj.user_id = d["user_id"]
        if "meta" in d: proj.meta = d["meta"]
        proj.save()

        # Optional owner update
        if "owner_key" in d:
            # clear if blank
            if not d["owner_key"]:
                for prev in proj.owner:
                    proj.owner.disconnect(prev)
            else:
                user = UserNode.nodes.first_or_none(key=d["owner_key"])
                if not user:
                    return Response({"error": f"owner_key '{d['owner_key']}' not found"}, status=400)
                for prev in proj.owner:
                    proj.owner.disconnect(prev)
                proj.owner.connect(user)

        # Optional members replace/additive (here: additive)
        if "member_keys" in d:
            for mk in d["member_keys"]:
                mu = UserNode.nodes.first_or_none(key=mk)
                if not mu:
                    return Response({"error": f"member_key '{mk}' not found"}, status=400)
                if not proj.members.is_connected(mu):
                    proj.members.connect(mu)

        return Response(serialize_project(proj))

# ------------------------
# Diagrams (scoped to Project)
# ------------------------
@extend_schema(
    tags=["Diagrams"],
    parameters=[OpenApiParameter("project_id", OpenApiTypes.STR, OpenApiParameter.PATH)],
    request=DiagramSerializer,
    responses={200: DiagramSerializer, 201: DiagramSerializer, 404: None}
)
class DiagramListCreateView(APIView):
    """
    GET  /api/projects/<project_id>/diagrams/
    POST /api/projects/<project_id>/diagrams/
    """
    def get(self, request, project_id):
        proj = get_project_or_404(project_id)
        diagrams = proj.diagrams.all()
        data = [{"key": d.key, "name": d.name, "meta": d.meta} for d in diagrams]
        return Response({"project": proj.key, "diagrams": data})

    def post(self, request, project_id):
        proj = get_project_or_404(project_id)
        s = DiagramSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        dia = Diagram.nodes.first_or_none(key=d["key"])
        if not dia:
            dia = Diagram(**d).save()
        else:
            dia.name = d.get("name", dia.name)
            dia.meta = d.get("meta", dia.meta or {})
            dia.save()

        if not proj.diagrams.is_connected(dia):
            proj.diagrams.connect(dia)

        return Response(
            {"project": proj.key, "diagram": {"key": dia.key, "name": dia.name, "meta": dia.meta}},
            status=status.HTTP_201_CREATED
        )
@extend_schema(
    tags=["Diagrams"],
    parameters=[
        OpenApiParameter("project_id", OpenApiTypes.STR, OpenApiParameter.PATH),
        OpenApiParameter("diagram_id", OpenApiTypes.STR, OpenApiParameter.PATH),
    ],
    responses={200: DiagramSerializer, 404: None}
)
class DiagramDetailView(APIView):
    """
    GET    /api/projects/<project_id>/diagrams/<diagram_id>/
    PATCH  /api/projects/<project_id>/diagrams/<diagram_id>/
    DELETE /api/projects/<project_id>/diagrams/<diagram_id>/
    """
    def get(self, request, project_id, diagram_id):
        proj = get_project_or_404(project_id)
        dia = get_diagram_or_404(diagram_id)
        ensure_diagram_in_project(proj, dia)
        return Response({"project": proj.key, "key": dia.key, "name": dia.name, "meta": dia.meta})

    def patch(self, request, project_id, diagram_id):
        proj = get_project_or_404(project_id)
        dia = get_diagram_or_404(diagram_id)
        ensure_diagram_in_project(proj, dia)

        s = DiagramSerializer(data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        if "name" in d: dia.name = d["name"]
        if "meta" in d: dia.meta = d["meta"]
        dia.save()

        return Response({"project": proj.key, "key": dia.key, "name": dia.name, "meta": dia.meta})

    def delete(self, request, project_id, diagram_id):
        proj = get_project_or_404(project_id)
        dia = get_diagram_or_404(diagram_id)
        ensure_diagram_in_project(proj, dia)

        # delete or detach nodes; here we delete nodes fully
        for node in dia.nodes:
            dia.nodes.disconnect(node)
            node.delete()
        proj.diagrams.disconnect(dia)
        dia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ------------------------
# Components (scoped to Diagram in Project)
# ------------------------

COMPONENT_CREATE_EXAMPLE = OpenApiExample(
    "Create component (external entity)",
    value={
        "id": "ext_user",
        "type": "external_entity",
        "position": {"x": 120, "y": 80},
        "size": {"width": 120, "height": 72},
        "data": {
            "text": "End User",
            "color": 4294967295,
            "borderColor": 4278190080,
            "borderWidth": 2,
            "textAlignment": "center",
            "textSize": 20
        }
    },
    request_only=True
)

@extend_schema(
    tags=["Components"],
    parameters=[
        OpenApiParameter("project_id", OpenApiTypes.STR, OpenApiParameter.PATH),
        OpenApiParameter("diagram_id", OpenApiTypes.STR, OpenApiParameter.PATH),
    ],
    request=ComponentSerializer,
    responses={200: ComponentSerializer, 201: ComponentSerializer, 404: None},
    examples=[COMPONENT_CREATE_EXAMPLE]
)
class ComponentListCreateUnderDiagramView(APIView):
    """
    GET  /api/projects/<project_id>/diagrams/<diagram_id>/components/
    POST /api/projects/<project_id>/diagrams/<diagram_id>/components/
    """
    def get(self, request, project_id, diagram_id):
        proj = get_project_or_404(project_id)
        dia = get_diagram_or_404(diagram_id)
        ensure_diagram_in_project(proj, dia)

        nodes = dia.nodes.all()
        results = [serialize_component(n) for n in nodes]
        return Response({"project": proj.key, "diagram": dia.key, "components": results})

    def post(self, request, project_id, diagram_id):
        proj = get_project_or_404(project_id)
        dia = get_diagram_or_404(diagram_id)
        ensure_diagram_in_project(proj, dia)

        s = ComponentSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        node_cls = TYPE_TO_NODE[d["type"]]
        key = d["id"]
        label = d["data"]["text"]

        node = node_cls.nodes.first_or_none(key=key) or node_cls(key=key, name=label)
        node.name = label
        node.pos_x = float(d["position"]["x"])
        node.pos_y = float(d["position"]["y"])
        node.width = float(d["size"]["width"])
        node.height = float(d["size"]["height"])
        node.ui = d["data"]
        node.save()

        if not dia.nodes.is_connected(node):
            dia.nodes.connect(node)

        return Response(
            {"project": proj.key, "diagram": dia.key, "component": serialize_component(node)},
            status=status.HTTP_201_CREATED
        )
@extend_schema(
    tags=["Components"],
    parameters=[
        OpenApiParameter("project_id", OpenApiTypes.STR, OpenApiParameter.PATH),
        OpenApiParameter("diagram_id", OpenApiTypes.STR, OpenApiParameter.PATH),
        OpenApiParameter("component_id", OpenApiTypes.STR, OpenApiParameter.PATH),
    ],
    responses={200: ComponentSerializer, 404: None}
)
class ComponentDetailUnderDiagramView(APIView):
    """
    GET    /api/projects/<project_id>/diagrams/<diagram_id>/components/<component_id>/
    PATCH  /api/projects/<project_id>/diagrams/<diagram_id>/components/<component_id>/
    DELETE /api/projects/<project_id>/diagrams/<diagram_id>/components/<component_id>/
    """
    def get(self, request, project_id, diagram_id, component_id):
        proj = get_project_or_404(project_id)
        dia = get_diagram_or_404(diagram_id)
        ensure_diagram_in_project(proj, dia)

        node = DFDNode.nodes.first_or_none(key=component_id)
        if not node or not dia.nodes.is_connected(node):
            raise Http404("Component not found in diagram")

        return Response(serialize_component(node))

    def patch(self, request, project_id, diagram_id, component_id):
        proj = get_project_or_404(project_id)
        dia = get_diagram_or_404(diagram_id)
        ensure_diagram_in_project(proj, dia)

        node = DFDNode.nodes.first_or_none(key=component_id)
        if not node or not dia.nodes.is_connected(node):
            raise Http404("Component not found in diagram")

        s = ComponentSerializer(data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        # Update fields only if present
        if "data" in d:
            if "text" in d["data"]:
                node.name = d["data"]["text"]
            node.ui = {**(node.ui or {}), **d["data"]}

        if "position" in d:
            if "x" in d["position"]: node.pos_x = float(d["position"]["x"])
            if "y" in d["position"]: node.pos_y = float(d["position"]["y"])

        if "size" in d:
            if "width" in d["size"]: node.width = float(d["size"]["width"])
            if "height" in d["size"]: node.height = float(d["size"]["height"])

        if "type" in d:
            # Optional: allow type change by re-creating as another class.
            # Safer default: reject type change to avoid class swap surprises.
            pass

        node.save()
        return Response(serialize_component(node))

    def delete(self, request, project_id, diagram_id, component_id):
        proj = get_project_or_404(project_id)
        dia = get_diagram_or_404(diagram_id)
        ensure_diagram_in_project(proj, dia)

        node = DFDNode.nodes.first_or_none(key=component_id)
        if not node or not dia.nodes.is_connected(node):
            raise Http404("Component not found in diagram")

        dia.nodes.disconnect(node)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
