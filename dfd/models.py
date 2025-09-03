from neomodel import (
    StructuredNode, StructuredRel, StringProperty, IntegerProperty, BooleanProperty,
    FloatProperty, UniqueIdProperty, RelationshipTo, RelationshipFrom, JSONProperty
)

# ---------- User (node) ----------
class UserNode(StructuredNode):
    uid = UniqueIdProperty()
    key = StringProperty(unique_index=True, required=True)   # e.g. "user_bassiman"
    email = StringProperty(index=True, required=True)
    name = StringProperty()
    role = StringProperty(default="member")                  # "owner", "member", "admin", etc.
    meta = JSONProperty(default={})

    # backrefs
    owns = RelationshipFrom('Project', 'OWNED_BY')           # projects owned by this user
    memberships = RelationshipFrom('Project', 'HAS_MEMBER')  # projects where this user is a member


# ---------- Relationship (edge) ----------
class DataFlow(StructuredRel):
    label = StringProperty(index=True, default="data_flow")
    description = StringProperty()
    payload_schema = StringProperty()
    protocol = StringProperty()
    method = StringProperty()
    frequency = StringProperty()
    pii = BooleanProperty(default=False)
    confidentiality = StringProperty(default="medium")
    integrity = StringProperty(default="medium")
    availability = StringProperty(default="medium")
    auth_required = BooleanProperty(default=True)
    encryption_in_transit = BooleanProperty(default=True)
    notes = StringProperty()

# ---------- Tenant containers ----------
class Project(StructuredNode):
    uid = UniqueIdProperty()
    key = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True)

    # legacy string; keep for now if you use it elsewhere
    user_id = StringProperty(index=True)

    meta = JSONProperty(default={})

    diagrams = RelationshipTo('Diagram', 'HAS_DIAGRAM')

    # NEW relations
    owner = RelationshipTo(UserNode, 'OWNED_BY')            # treat as single logically
    members = RelationshipTo(UserNode, 'HAS_MEMBER')


class Diagram(StructuredNode):
    uid = UniqueIdProperty()
    key = StringProperty(unique_index=True, required=True)   # e.g. "dfd_login_v1"
    name = StringProperty(required=True)
    meta = JSONProperty(default={})

    project = RelationshipFrom(Project, 'HAS_DIAGRAM')
    nodes = RelationshipTo('DFDNode', 'HAS_NODE')            # contains all nodes of this diagram

# ---------- Base DFD nodes ----------
class DFDNode(StructuredNode):
    uid = UniqueIdProperty()
    key = StringProperty(unique_index=True, required=True)
    name = StringProperty(index=True, required=True)
    description = StringProperty()
    dfd_level = IntegerProperty(default=0)
    zone = StringProperty()
    owner = StringProperty()
    criticality = StringProperty(default="medium")

    # UI / layout props (round-trip to canvas)
    pos_x = FloatProperty(default=0.0)
    pos_y = FloatProperty(default=0.0)
    width = FloatProperty(default=120.0)
    height = FloatProperty(default=72.0)
    ui = JSONProperty(default={})

    # containment and flows
    diagram = RelationshipFrom(Diagram, 'HAS_NODE')
    inbound = RelationshipFrom('DFDNode', 'DATA_FLOW', model=DataFlow)
    outbound = RelationshipTo('DFDNode', 'DATA_FLOW', model=DataFlow)

class Process(DFDNode):
    tech = StringProperty()

class ExternalEntity(DFDNode):
    actor_type = StringProperty(default="user")

class DataStore(DFDNode):
    store_type = StringProperty(default="database")
    technology = StringProperty()
    retention_days = IntegerProperty(default=0)
    encryption_at_rest = BooleanProperty(default=True)
    backups_enabled = BooleanProperty(default=True)
    rto_hours = FloatProperty(default=4.0)
    rpo_hours = FloatProperty(default=1.0)
