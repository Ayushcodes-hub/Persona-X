from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from backend.app.core.database import get_db
from backend.app.models.person import Person
from backend.app.models.dossier import Dossier
from backend.app.models.timeline import TimelineEvent
from backend.app.models.statement import Statement
from backend.app.models.initiative import Initiative
from backend.app.models.claim import Claim
from backend.app.models.evidence import Evidence
from backend.app.models.source import Source
from backend.app.models.research_job import ResearchJob
from backend.app.models.research_result import ResearchResult
from backend.app.models.research_query import ResearchQuery

from engine.identity.discovery import identity_discovery
from engine.political.service import PoliticalAnalysisService
from engine.political.schemas import PoliticalEvidence
from engine.profession.service import ProfessionAnalysisService
from engine.profession.schemas import ProfessionEvidence

router = APIRouter(
    prefix="/persons",
    tags=["persons"],
)


@router.get("/search")
def search_persons(
    q: str = Query(..., min_length=1, description="Person name to search"),
    include_external: bool = Query(True, description="Whether to include live Wikidata/Wikipedia candidate disambiguation"),
    db: Session = Depends(get_db),
):
    query_str = q.strip()
    db_matches = (
        db.query(Person)
        .filter(
            or_(
                Person.canonical_name.ilike(f"%{query_str}%"),
                Person.aliases.ilike(f"%{query_str}%"),
            )
        )
        .limit(10)
        .all()
    )

    db_results = []
    for p in db_matches:
        dossier = db.query(Dossier).filter(Dossier.person_id == p.id).order_by(Dossier.version.desc()).first()
        db_results.append({
            "id": p.id,
            "canonical_name": p.canonical_name,
            "primary_profession": p.primary_profession,
            "identity_status": p.identity_status,
            "identity_confidence": p.identity_confidence,
            "has_dossier": dossier is not None,
            "dossier_id": dossier.id if dossier else None,
            "is_local": True,
        })

    external_candidates = []
    if include_external:
        try:
            candidates = identity_discovery.discover_candidates(query_str, limit=6)
            for c in candidates:
                external_candidates.append({
                    "wikidata_id": c.wikidata_id,
                    "label": c.label,
                    "description": c.description,
                    "birth_year": c.birth_year,
                    "professions": c.professions,
                    "wikipedia_url": c.wikipedia_url,
                    "match_score": c.match_score,
                    "is_local": False,
                })
        except Exception:
            external_candidates = []

    return {
        "query": query_str,
        "local_count": len(db_results),
        "local_persons": db_results,
        "external_candidates": external_candidates,
    }


@router.get("")
def list_persons(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    total = db.query(func.count(Person.id)).scalar() or 0
    persons = db.query(Person).order_by(Person.canonical_name.asc()).offset(offset).limit(limit).all()

    items = []
    for p in persons:
        dossier = db.query(Dossier).filter(Dossier.person_id == p.id).order_by(Dossier.version.desc()).first()
        sources_count = (
            db.query(func.count(func.distinct(Source.id)))
            .join(ResearchResult, ResearchResult.source_id == Source.id)
            .join(ResearchQuery, ResearchQuery.id == ResearchResult.research_query_id)
            .join(ResearchJob, ResearchJob.id == ResearchQuery.research_job_id)
            .filter(ResearchJob.person_id == p.id)
            .scalar() or 0
        )
        evidence_count = db.query(func.count(Evidence.id)).filter(Evidence.person_id == p.id).scalar() or 0
        timeline_count = db.query(func.count(TimelineEvent.id)).filter(TimelineEvent.person_id == p.id).scalar() or 0

        items.append({
            "id": p.id,
            "canonical_name": p.canonical_name,
            "primary_profession": p.primary_profession,
            "identity_status": p.identity_status,
            "identity_confidence": p.identity_confidence,
            "has_dossier": dossier is not None,
            "dossier_id": dossier.id if dossier else None,
            "dossier_completeness": dossier.completeness_score if dossier else None,
            "counts": {
                "sources": sources_count,
                "evidence": evidence_count,
                "timeline_events": timeline_count,
            },
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": items,
    }


@router.get("/{person_id}")
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found.")

    dossier = db.query(Dossier).filter(Dossier.person_id == person_id).order_by(Dossier.version.desc()).first()
    sources_count = (
        db.query(func.count(func.distinct(Source.id)))
        .join(ResearchResult, ResearchResult.source_id == Source.id)
        .join(ResearchQuery, ResearchQuery.id == ResearchResult.research_query_id)
        .join(ResearchJob, ResearchJob.id == ResearchQuery.research_job_id)
        .filter(ResearchJob.person_id == person.id)
        .scalar() or 0
    )
    evidence_count = db.query(func.count(Evidence.id)).filter(Evidence.person_id == person.id).scalar() or 0
    statements_count = db.query(func.count(Statement.id)).filter(Statement.person_id == person.id).scalar() or 0
    timeline_count = db.query(func.count(TimelineEvent.id)).filter(TimelineEvent.person_id == person.id).scalar() or 0
    initiatives_count = db.query(func.count(Initiative.id)).filter(Initiative.person_id == person.id).scalar() or 0

    return {
        "id": person.id,
        "canonical_name": person.canonical_name,
        "primary_profession": person.primary_profession,
        "identity_status": person.identity_status,
        "identity_confidence": person.identity_confidence,
        "aliases": person.aliases,
        "has_dossier": dossier is not None,
        "latest_dossier_id": dossier.id if dossier else None,
        "counts": {
            "sources": sources_count,
            "evidence": evidence_count,
            "statements": statements_count,
            "timeline_events": timeline_count,
            "initiatives": initiatives_count,
        },
        "created_at": person.created_at.isoformat() if person.created_at else None,
        "updated_at": person.updated_at.isoformat() if person.updated_at else None,
    }


@router.get("/{person_id}/dossier")
def get_person_dossier(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found.")

    dossier = (
        db.query(Dossier)
        .filter(Dossier.person_id == person_id)
        .order_by(Dossier.version.desc())
        .first()
    )
    if not dossier:
        raise HTTPException(status_code=404, detail="No dossier found for this person.")

    return {
        "dossier_id": dossier.id,
        "person_id": dossier.person_id,
        "canonical_name": person.canonical_name,
        "research_job_id": dossier.research_job_id,
        "version": dossier.version,
        "status": dossier.status,
        "title": dossier.title,
        "executive_summary": dossier.executive_summary,
        "dossier_content": dossier.dossier_content,
        "source_count": dossier.source_count,
        "evidence_count": dossier.evidence_count,
        "completeness_score": dossier.completeness_score,
        "created_at": dossier.created_at.isoformat() if dossier.created_at else None,
        "updated_at": dossier.updated_at.isoformat() if dossier.updated_at else None,
    }


@router.get("/{person_id}/timeline")
def get_person_timeline(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found.")

    events = (
        db.query(TimelineEvent)
        .filter(TimelineEvent.person_id == person_id)
        .order_by(TimelineEvent.start_date.asc().nulls_last(), TimelineEvent.id.asc())
        .all()
    )

    items = []
    for e in events:
        evidence = db.query(Evidence).filter(Evidence.id == e.evidence_id).first() if e.evidence_id else None
        source = db.query(Source).filter(Source.id == evidence.source_id).first() if evidence and evidence.source_id else None

        items.append({
            "id": e.id,
            "event_type": e.event_type,
            "title": e.title,
            "description": e.description,
            "start_date": e.start_date.isoformat() if e.start_date else None,
            "end_date": e.end_date.isoformat() if e.end_date else None,
            "organization": e.organization,
            "location": e.location,
            "status": e.status,
            "confidence": e.confidence,
            "evidence_id": e.evidence_id,
            "source": {
                "id": source.id,
                "title": source.title,
                "url": source.url,
                "source_tier": source.source_tier,
            } if source else None,
        })

    return {
        "person_id": person_id,
        "canonical_name": person.canonical_name,
        "count": len(items),
        "events": items,
    }


@router.get("/{person_id}/statements")
def get_person_statements(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found.")

    statements = (
        db.query(Statement)
        .filter(Statement.person_id == person_id)
        .order_by(Statement.statement_date.desc().nulls_last(), Statement.id.desc())
        .all()
    )

    items = []
    for s in statements:
        source = db.query(Source).filter(Source.id == s.source_id).first() if s.source_id else None
        items.append({
            "id": s.id,
            "statement_type": s.statement_type,
            "text": s.text,
            "paraphrase": s.paraphrase,
            "topic": s.topic,
            "context": s.context,
            "statement_date": s.statement_date.isoformat() if s.statement_date else None,
            "attribution_status": s.attribution_status,
            "confidence": s.confidence,
            "evidence_id": s.evidence_id,
            "source": {
                "id": source.id,
                "title": source.title,
                "url": source.url,
                "source_tier": source.source_tier,
            } if source else None,
        })

    return {
        "person_id": person_id,
        "canonical_name": person.canonical_name,
        "count": len(items),
        "statements": items,
    }


@router.get("/{person_id}/initiatives")
def get_person_initiatives(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found.")

    initiatives = (
        db.query(Initiative)
        .filter(Initiative.person_id == person_id)
        .order_by(Initiative.id.desc())
        .all()
    )

    items = []
    for init in initiatives:
        evidence = db.query(Evidence).filter(Evidence.id == init.evidence_id).first() if init.evidence_id else None
        source = db.query(Source).filter(Source.id == evidence.source_id).first() if evidence and evidence.source_id else None

        items.append({
            "id": init.id,
            "name": init.name,
            "initiative_type": init.initiative_type,
            "description": init.description,
            "objective": init.objective,
            "lifecycle_stage": init.lifecycle_stage,
            "start_date": init.start_date.isoformat() if init.start_date else None,
            "end_date": init.end_date.isoformat() if init.end_date else None,
            "evidence_id": init.evidence_id,
            "source": {
                "id": source.id,
                "title": source.title,
                "url": source.url,
            } if source else None,
        })

    return {
        "person_id": person_id,
        "canonical_name": person.canonical_name,
        "count": len(items),
        "initiatives": items,
    }


@router.get("/{person_id}/sources")
def get_person_sources(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found.")

    sources = (
        db.query(Source)
        .join(ResearchResult, ResearchResult.source_id == Source.id)
        .join(ResearchQuery, ResearchQuery.id == ResearchResult.research_query_id)
        .join(ResearchJob, ResearchJob.id == ResearchQuery.research_job_id)
        .filter(ResearchJob.person_id == person.id)
        .distinct()
        .all()
    )

    items = []
    for s in sources:
        items.append({
            "id": s.id,
            "title": s.title,
            "publisher": s.publisher,
            "url": s.url,
            "domain": s.publisher or (s.url.split("/")[2] if "://" in s.url else ""),
            "source_type": s.source_type,
            "source_tier": s.source_tier,
            "reliability_score": s.reliability_score,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })

    return {
        "person_id": person_id,
        "canonical_name": person.canonical_name,
        "count": len(items),
        "sources": items,
    }


@router.get("/{person_id}/graph")
def get_person_graph(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found.")

    nodes = []
    edges = []
    seen_nodes = set()

    def add_node(nid, ntype, label, confidence=1.0, metadata=None):
        if nid not in seen_nodes:
            seen_nodes.add(nid)
            nodes.append({
                "id": nid,
                "type": ntype,
                "label": label[:100] if label else "Untitled",
                "confidence": confidence,
                "metadata": metadata or {},
            })

    def add_edge(src, tgt, edge_type, confidence=1.0):
        edges.append({
            "source": src,
            "target": tgt,
            "type": edge_type,
            "confidence": confidence,
        })

    # 1. Person root node
    p_nid = f"person:{person.id}"
    add_node(p_nid, "person", person.canonical_name, person.identity_confidence, {
        "primary_profession": person.primary_profession,
    })

    # 2. Sources
    sources = (
        db.query(Source)
        .join(ResearchResult, ResearchResult.source_id == Source.id)
        .join(ResearchQuery, ResearchQuery.id == ResearchResult.research_query_id)
        .join(ResearchJob, ResearchJob.id == ResearchQuery.research_job_id)
        .filter(ResearchJob.person_id == person.id)
        .distinct()
        .all()
    )
    for s in sources:
        s_nid = f"source:{s.id}"
        add_node(s_nid, "source", s.title or s.url, s.reliability_score, {
            "url": s.url,
            "tier": s.source_tier,
        })
        add_edge(p_nid, s_nid, "source_for", s.reliability_score)

    # 3. Evidence
    evidence_items = db.query(Evidence).filter(Evidence.person_id == person.id).all()
    for ev in evidence_items:
        ev_nid = f"evidence:{ev.id}"
        add_node(ev_nid, "evidence", ev.normalized_claim or (ev.extracted_text[:80] if ev.extracted_text else "Evidence"), ev.confidence, {
            "type": ev.evidence_type,
            "status": ev.verification_status,
        })
        add_edge(p_nid, ev_nid, "evidences", ev.confidence)
        if ev.source_id:
            s_nid = f"source:{ev.source_id}"
            if s_nid in seen_nodes:
                add_edge(s_nid, ev_nid, "evidences", ev.confidence)

    # 4. Claims
    claims = db.query(Claim).filter(Claim.person_id == person.id).all()
    for c in claims:
        c_nid = f"claim:{c.id}"
        add_node(c_nid, "claim", c.claim_text, c.confidence, {
            "topic": c.topic,
            "status": c.verification_status,
        })
        if c.evidence_id:
            ev_nid = f"evidence:{c.evidence_id}"
            if ev_nid in seen_nodes:
                add_edge(ev_nid, c_nid, "derived_from", c.confidence)

    # 5. Statements
    statements = db.query(Statement).filter(Statement.person_id == person.id).all()
    for st in statements:
        st_nid = f"statement:{st.id}"
        add_node(st_nid, "statement", st.text, st.confidence, {
            "type": st.statement_type,
            "topic": st.topic,
        })
        if st.evidence_id:
            ev_nid = f"evidence:{st.evidence_id}"
            if ev_nid in seen_nodes:
                add_edge(ev_nid, st_nid, "asserts", st.confidence)
        elif st.source_id:
            s_nid = f"source:{st.source_id}"
            if s_nid in seen_nodes:
                add_edge(s_nid, st_nid, "asserts", st.confidence)

    # 6. Timeline Events
    timeline_events = db.query(TimelineEvent).filter(TimelineEvent.person_id == person.id).all()
    for te in timeline_events:
        te_nid = f"timeline:{te.id}"
        add_node(te_nid, "timeline_event", te.title, te.confidence, {
            "date": te.start_date.isoformat() if te.start_date else None,
            "type": te.event_type,
        })
        add_edge(p_nid, te_nid, "has_event", te.confidence)
        if te.evidence_id:
            ev_nid = f"evidence:{te.evidence_id}"
            if ev_nid in seen_nodes:
                add_edge(ev_nid, te_nid, "derived_from", te.confidence)

    # 7. Initiatives
    initiatives = db.query(Initiative).filter(Initiative.person_id == person.id).all()
    for init in initiatives:
        init_nid = f"initiative:{init.id}"
        add_node(init_nid, "initiative", init.name, 0.9, {
            "stage": init.lifecycle_stage,
            "type": init.initiative_type,
        })
        add_edge(p_nid, init_nid, "has_initiative", 0.9)
        if init.evidence_id:
            ev_nid = f"evidence:{init.evidence_id}"
            if ev_nid in seen_nodes:
                add_edge(ev_nid, init_nid, "derived_from", 0.9)

    return {
        "person_id": person.id,
        "canonical_name": person.canonical_name,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


@router.get("/{person_id}/analysis/political")
def get_person_political_analysis(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found.")

    statements = db.query(Statement).filter(Statement.person_id == person.id).all()
    political_evidence = []
    for s in statements:
        political_evidence.append(
            PoliticalEvidence(
                evidence_type="political_interview" if s.statement_type in {"interview", "political_interview"} else "policy_statement",
                text=s.text,
                topic=s.topic,
                issue=s.topic,
                evidence_id=s.evidence_id,
                source_id=s.source_id,
                statement_id=s.id,
                event_date=s.statement_date.isoformat() if s.statement_date else None,
                verification_status=s.attribution_status,
                attribution_status=s.attribution_status,
                confidence=s.confidence,
            )
        )

    service = PoliticalAnalysisService()
    analysis = service.analyze(person.canonical_name, political_evidence)

    spectrum_data = None
    if analysis.spectrum:
        spectrum_data = {
            "applicable": analysis.spectrum.applicable,
            "score": analysis.spectrum.spectrum_score,
            "label": analysis.spectrum.spectrum_label,
            "economic_axis": analysis.spectrum.economic_axis,
            "social_axis": analysis.spectrum.social_axis,
            "governance_axis": analysis.spectrum.governance_axis,
            "foreign_policy_axis": analysis.spectrum.foreign_policy_axis,
            "confidence": analysis.spectrum.confidence,
            "rationale": analysis.spectrum.rationale,
            "key_indicators": analysis.spectrum.key_indicators,
        }

    dimensions_data = []
    for d in analysis.dimensions:
        dimensions_data.append({
            "name": d.name,
            "confidence": d.confidence,
            "evidence_count": d.evidence_count,
        })

    return {
        "person_id": person.id,
        "canonical_name": person.canonical_name,
        "applicable": analysis.applicable,
        "evidence_count": analysis.evidence_count,
        "sufficiency": {
            "sufficient": analysis.sufficiency.sufficient,
            "evidence_count": analysis.sufficiency.evidence_count,
            "qualifying_evidence_count": analysis.sufficiency.qualifying_evidence_count,
            "dimensions_covered": analysis.sufficiency.dimensions_covered,
            "confidence": analysis.sufficiency.confidence,
            "reason": analysis.sufficiency.reason,
        },
        "spectrum": spectrum_data,
        "dimensions": dimensions_data,
        "limitations": analysis.limitations,
    }


@router.get("/{person_id}/analysis/profession")
def get_person_profession_analysis(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found.")

    evidence_items = db.query(Evidence).filter(Evidence.person_id == person.id).all()
    prof_evidence = []
    for item in evidence_items:
        prof_evidence.append(
            ProfessionEvidence(
                category="source_evidence",
                value=item.extracted_text or "",
                evidence_id=item.id,
                source_id=item.source_id,
                confidence=item.confidence,
            )
        )

    professions = [person.primary_profession] if person.primary_profession else ["general"]
    service = ProfessionAnalysisService()
    analysis = service.analyze(person.canonical_name, professions, prof_evidence)

    profiles_data = []
    for p in analysis.profiles:
        profiles_data.append({
            "profession": p.profession,
            "seniority": getattr(p, "seniority", "established"),
            "domains": getattr(p, "domains", []),
            "summary": getattr(p, "summary", ""),
        })

    return {
        "person_id": person.id,
        "canonical_name": person.canonical_name,
        "professions": professions,
        "confidence": analysis.confidence,
        "profiles": profiles_data,
        "findings_count": len(analysis.findings),
    }
