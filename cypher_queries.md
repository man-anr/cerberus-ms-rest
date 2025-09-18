# Cypher Queries for Complete Threat Modeling Diagram

This document contains Cypher queries to visualize and analyze the complete threat modeling diagram created in Neo4j.

## 1. View Complete Diagram Structure

```cypher
// Get all components in the e-commerce diagram
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_ELEMENT|HAS_THREAT|HAS_TRUST_BOUNDARY]->(comp)
RETURN 
  labels(comp) as ComponentType,
  comp.name as Name,
  comp.key as Key,
  comp.criticality as Criticality,
  comp.pos_x as X,
  comp.pos_y as Y
ORDER BY labels(comp), comp.name;
```

## 2. Visualize All Components with Relationships

```cypher
// Visualize the complete diagram with all relationships
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_ELEMENT|HAS_THREAT|HAS_TRUST_BOUNDARY]->(comp)
OPTIONAL MATCH (comp)-[r]->(target)
RETURN comp, r, target;
```

## 3. View All STRIDE Threats

```cypher
// Get all threats organized by STRIDE type
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_THREAT]->(t:ThreatNode)
RETURN 
  t.threat_type as STRIDEType,
  t.name as ThreatName,
  t.criticality as Criticality,
  t.risk_level as RiskLevel,
  t.status as Status,
  t.impact as Impact,
  t.likelihood as Likelihood,
  t.mitigation_strategies as Mitigations
ORDER BY t.criticality DESC, t.threat_type;
```

## 4. View Threat-Component Relationships

```cypher
// See which components are threatened by each threat
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_THREAT]->(t:ThreatNode)
MATCH (t)-[:THREATENS]->(comp)
RETURN 
  t.name as Threat,
  t.threat_type as STRIDEType,
  t.criticality as ThreatCriticality,
  labels(comp) as ComponentType,
  comp.name as ComponentName,
  comp.criticality as ComponentCriticality
ORDER BY t.criticality DESC, t.name;
```

## 5. View Trust Boundaries and Protected Components

```cypher
// See trust boundaries and what they protect
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_TRUST_BOUNDARY]->(tb:TrustBoundaryNode)
MATCH (tb)-[:PROTECTS]->(comp)
RETURN 
  tb.name as TrustBoundary,
  tb.boundary_type as BoundaryType,
  tb.criticality as BoundaryCriticality,
  tb.security_controls as SecurityControls,
  labels(comp) as ComponentType,
  comp.name as ProtectedComponent,
  comp.criticality as ComponentCriticality
ORDER BY tb.criticality DESC, tb.name;
```

## 6. View Data Flow Relationships

```cypher
// See all data flows between components
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_ELEMENT]->(source)
MATCH (source)-[r:DATA_FLOW]->(target)
RETURN 
  labels(source) as SourceType,
  source.name as SourceComponent,
  r.label as FlowLabel,
  r.protocol as Protocol,
  r.auth_required as AuthRequired,
  labels(target) as TargetType,
  target.name as TargetComponent
ORDER BY source.name, r.label;
```

## 7. Risk Analysis by Component

```cypher
// Analyze risk by component - see which components are most threatened
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_ELEMENT]->(comp)
OPTIONAL MATCH (comp)<-[:THREATENS]-(t:ThreatNode)
WITH comp, collect(t) as threats
RETURN 
  labels(comp) as ComponentType,
  comp.name as ComponentName,
  comp.criticality as ComponentCriticality,
  size(threats) as ThreatCount,
  [t in threats | t.threat_type] as ThreatTypes,
  [t in threats | t.criticality] as ThreatCriticalities
ORDER BY size(threats) DESC, comp.criticality DESC;
```

## 8. Critical Threats Analysis

```cypher
// Focus on critical and high-risk threats
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_THREAT]->(t:ThreatNode)
WHERE t.criticality IN ['critical', 'high'] OR t.risk_level IN ['critical', 'high']
MATCH (t)-[:THREATENS]->(comp)
RETURN 
  t.name as Threat,
  t.threat_type as STRIDEType,
  t.criticality as Criticality,
  t.risk_level as RiskLevel,
  t.status as Status,
  t.assigned_to as AssignedTo,
  t.due_date as DueDate,
  collect(comp.name) as AffectedComponents,
  t.mitigation_strategies as Mitigations
ORDER BY 
  CASE t.criticality 
    WHEN 'critical' THEN 1 
    WHEN 'high' THEN 2 
    ELSE 3 
  END,
  t.due_date;
```

## 9. Trust Boundary Security Analysis

```cypher
// Analyze security controls across trust boundaries
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_TRUST_BOUNDARY]->(tb:TrustBoundaryNode)
OPTIONAL MATCH (tb)-[:PROTECTS]->(comp)
WITH tb, collect(comp) as protected_components
RETURN 
  tb.name as TrustBoundary,
  tb.boundary_type as BoundaryType,
  tb.criticality as Criticality,
  tb.security_controls as SecurityControls,
  size(protected_components) as ProtectedComponentCount,
  [c in protected_components | c.name] as ProtectedComponents
ORDER BY tb.criticality DESC;
```

## 10. Complete Visual Graph

```cypher
// Get everything for a complete visual representation
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_ELEMENT|HAS_THREAT|HAS_TRUST_BOUNDARY]->(comp)
OPTIONAL MATCH (comp)-[r]->(target)
OPTIONAL MATCH (comp)<-[r2]-(source)
RETURN comp, r, target, r2, source;
```

## 11. Component Statistics

```cypher
// Get statistics about the diagram
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_ELEMENT|HAS_THREAT|HAS_TRUST_BOUNDARY]->(comp)
WITH labels(comp)[0] as ComponentType, count(comp) as Count
RETURN ComponentType, Count
ORDER BY Count DESC;
```

## 12. Threat Coverage Analysis

```cypher
// Analyze STRIDE threat coverage
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_THREAT]->(t:ThreatNode)
WITH t.threat_type as STRIDEType, count(t) as ThreatCount, collect(t.name) as Threats
RETURN 
  STRIDEType,
  ThreatCount,
  Threats
ORDER BY ThreatCount DESC;
```

## 13. High-Risk Component Identification

```cypher
// Identify components with the highest risk exposure
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_ELEMENT]->(comp)
OPTIONAL MATCH (comp)<-[:THREATENS]-(t:ThreatNode)
WITH comp, collect(t) as threats
WITH comp, threats, 
     size([t in threats WHERE t.criticality = 'critical']) as critical_threats,
     size([t in threats WHERE t.criticality = 'high']) as high_threats
WHERE critical_threats > 0 OR high_threats > 0
RETURN 
  labels(comp) as ComponentType,
  comp.name as ComponentName,
  comp.criticality as ComponentCriticality,
  critical_threats as CriticalThreats,
  high_threats as HighThreats,
  size(threats) as TotalThreats,
  [t in threats | t.name] as ThreatNames
ORDER BY critical_threats DESC, high_threats DESC, size(threats) DESC;
```

## 14. Mitigation Strategy Analysis

```cypher
// Analyze mitigation strategies across all threats
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_THREAT]->(t:ThreatNode)
UNWIND t.mitigation_strategies as mitigation
RETURN 
  mitigation as MitigationStrategy,
  count(*) as UsageCount,
  collect(DISTINCT t.name) as UsedInThreats
ORDER BY UsageCount DESC;
```

## 15. Timeline Analysis

```cypher
// Analyze threats by due date and status
MATCH (p:Project {key: "ecommerce_threat_model"})-[:HAS_DIAGRAM]->(d:Diagram {key: "ecommerce_dfd_v1"})
MATCH (d)-[:HAS_THREAT]->(t:ThreatNode)
RETURN 
  t.name as Threat,
  t.threat_type as STRIDEType,
  t.status as Status,
  t.criticality as Criticality,
  t.due_date as DueDate,
  t.assigned_to as AssignedTo,
  t.owner as Owner
ORDER BY t.due_date, t.criticality DESC;
```

## Usage Instructions

1. **Run the Python script first** to create the diagram:
   ```bash
   cd /Users/bassimananuar/Documents/Projects/cerberus-ms-rest
   python create_complete_diagram.py
   ```

2. **Open Neo4j Browser** (usually at http://localhost:7474)

3. **Copy and paste any of the above queries** into the Neo4j Browser query editor

4. **Run the queries** to visualize different aspects of the threat model

5. **Use the graph visualization** in Neo4j Browser to see the complete diagram with all relationships

## Key Features of This Diagram

- **Complete STRIDE Coverage**: All 6 STRIDE threat types represented
- **Realistic E-commerce Scenario**: Based on a real-world application architecture
- **Trust Boundaries**: Network, DMZ, and internal boundaries with security controls
- **Component Relationships**: Data flows, threat relationships, and boundary protections
- **Risk Analysis**: Criticality levels, risk assessments, and mitigation strategies
- **Timeline Management**: Due dates, assignments, and status tracking

This comprehensive diagram provides a complete example of threat modeling in action with all the components, relationships, and analysis capabilities you need to understand the full system.
