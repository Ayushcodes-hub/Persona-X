"""initial_baseline_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-03 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('is_admin', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # 2. persons
    op.create_table(
        'persons',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('canonical_name', sa.String(length=300), nullable=False),
        sa.Column('aliases', sa.Text(), nullable=True),
        sa.Column('primary_profession', sa.String(length=150), nullable=True),
        sa.Column('professions', sa.Text(), nullable=True),
        sa.Column('nationality', sa.String(length=150), nullable=True),
        sa.Column('birth_date', sa.String(length=50), nullable=True),
        sa.Column('active_from', sa.String(length=50), nullable=True),
        sa.Column('active_to', sa.String(length=50), nullable=True),
        sa.Column('biography_summary', sa.Text(), nullable=True),
        sa.Column('identity_confidence', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('identity_status', sa.String(length=50), server_default='unverified', nullable=False),
        sa.Column('ambiguity_notes', sa.Text(), nullable=True),
        sa.Column('wikidata_id', sa.String(length=50), nullable=True),
        sa.Column('wikipedia_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_persons_canonical_name', 'persons', ['canonical_name'], unique=False)
    op.create_index('ix_persons_wikidata_id', 'persons', ['wikidata_id'], unique=False)

    # 3. research_jobs
    op.create_table(
        'research_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('job_type', sa.String(length=50), server_default='full_research', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='queued', nullable=False),
        sa.Column('requested_scope', sa.JSON(), nullable=True),
        sa.Column('query_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('source_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('evidence_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('current_stage', sa.String(length=100), server_default='pending', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_research_jobs_status', 'research_jobs', ['status'], unique=False)
    op.create_index('ix_research_jobs_person_id', 'research_jobs', ['person_id'], unique=False)

    # 4. research_events
    op.create_table(
        'research_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('stage', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['research_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_research_events_job_id', 'research_events', ['job_id'], unique=False)
    op.create_index('ix_research_events_stage', 'research_events', ['stage'], unique=False)
    op.create_index('ix_research_events_created_at', 'research_events', ['created_at'], unique=False)
    op.create_index('ix_research_events_job_id_id', 'research_events', ['job_id', 'id'], unique=False)

    # 5. research_queries
    op.create_table(
        'research_queries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('research_job_id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('query_type', sa.String(length=50), server_default='browser_search', nullable=False),
        sa.Column('profession_context', sa.String(length=100), nullable=True),
        sa.Column('topic', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='pending', nullable=False),
        sa.Column('result_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('priority', sa.Integer(), server_default='5', nullable=False),
        sa.Column('execution_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['research_job_id'], ['research_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_research_queries_job_id', 'research_queries', ['research_job_id'], unique=False)
    op.create_index('ix_research_queries_status', 'research_queries', ['status'], unique=False)

    # 6. sources
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('publisher', sa.String(length=300), nullable=True),
        sa.Column('source_type', sa.String(length=100), nullable=False),
        sa.Column('source_tier', sa.Integer(), server_default='3', nullable=False),
        sa.Column('author', sa.String(length=300), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('retrieved_at', sa.DateTime(), nullable=True),
        sa.Column('content_hash', sa.String(length=128), nullable=True),
        sa.Column('reliability_score', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sources_url', 'sources', ['url'], unique=True)
    op.create_index('ix_sources_source_tier', 'sources', ['source_tier'], unique=False)

    # 7. research_results
    op.create_table(
        'research_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('research_query_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('result_rank', sa.Integer(), server_default='1', nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('snippet', sa.Text(), nullable=True),
        sa.Column('relevance_score', sa.Float(), server_default='0.5', nullable=False),
        sa.Column('discovery_method', sa.String(length=100), server_default='browser_search', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='discovered', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['research_query_id'], ['research_queries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_research_results_query_id', 'research_results', ['research_query_id'], unique=False)
    op.create_index('ix_research_results_source_id', 'research_results', ['source_id'], unique=False)

    # 8. source_captures
    op.create_table(
        'source_captures',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('capture_version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('retrieved_at', sa.DateTime(), nullable=False),
        sa.Column('http_status', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('storage_key', sa.Text(), nullable=True),
        sa.Column('archive_url', sa.Text(), nullable=True),
        sa.Column('capture_status', sa.String(length=50), server_default='captured', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_source_captures_source_id', 'source_captures', ['source_id'], unique=False)
    op.create_index('ix_source_captures_content_hash', 'source_captures', ['content_hash'], unique=False)

    # 9. evidence
    op.create_table(
        'evidence',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('source_capture_id', sa.Integer(), nullable=True),
        sa.Column('evidence_type', sa.String(length=100), server_default='textual', nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=False),
        sa.Column('normalized_claim', sa.Text(), nullable=True),
        sa.Column('verbatim_span', sa.Text(), nullable=True),
        sa.Column('source_locator', sa.Text(), nullable=True),
        sa.Column('event_date', sa.DateTime(), nullable=True),
        sa.Column('verification_status', sa.String(length=50), server_default='unverified', nullable=False),
        sa.Column('confidence', sa.Float(), server_default='0.5', nullable=False),
        sa.Column('extraction_method', sa.String(length=100), nullable=True),
        sa.Column('extraction_model', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['source_capture_id'], ['source_captures.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_evidence_person_id', 'evidence', ['person_id'], unique=False)
    op.create_index('ix_evidence_source_id', 'evidence', ['source_id'], unique=False)
    op.create_index('ix_evidence_evidence_type', 'evidence', ['evidence_type'], unique=False)

    # 10. statements
    op.create_table(
        'statements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('evidence_id', sa.Integer(), nullable=True),
        sa.Column('statement_type', sa.String(length=50), server_default='direct_quote', nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('paraphrase', sa.Text(), nullable=True),
        sa.Column('topic', sa.String(length=100), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('statement_date', sa.DateTime(), nullable=True),
        sa.Column('attribution_status', sa.String(length=50), server_default='attributed', nullable=False),
        sa.Column('confidence', sa.Float(), server_default='0.5', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_statements_person_id', 'statements', ['person_id'], unique=False)
    op.create_index('ix_statements_statement_type', 'statements', ['statement_type'], unique=False)

    # 11. claims
    op.create_table(
        'claims',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('evidence_id', sa.Integer(), nullable=True),
        sa.Column('statement_id', sa.Integer(), nullable=True),
        sa.Column('claim_type', sa.String(length=100), server_default='factual', nullable=False),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('topic', sa.String(length=100), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('predicate', sa.String(length=300), nullable=True),
        sa.Column('object_value', sa.Text(), nullable=True),
        sa.Column('verification_status', sa.String(length=50), server_default='unverified', nullable=False),
        sa.Column('confidence', sa.Float(), server_default='0.5', nullable=False),
        sa.Column('analyst_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['statement_id'], ['statements.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_claims_person_id', 'claims', ['person_id'], unique=False)
    op.create_index('ix_claims_topic', 'claims', ['topic'], unique=False)

    # 12. initiatives
    op.create_table(
        'initiatives',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('evidence_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('initiative_type', sa.String(length=100), server_default='project', nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('lifecycle_stage', sa.String(length=50), server_default='proposed', nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('organization', sa.String(length=500), nullable=True),
        sa.Column('location', sa.String(length=500), nullable=True),
        sa.Column('outcome', sa.Text(), nullable=True),
        sa.Column('evaluation', sa.Text(), nullable=True),
        sa.Column('evidence_confidence', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('verification_status', sa.String(length=50), server_default='unverified', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_initiatives_person_id', 'initiatives', ['person_id'], unique=False)

    # 13. timeline_events
    op.create_table(
        'timeline_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('evidence_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=100), server_default='career_milestone', nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('organization', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='documented', nullable=False),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_timeline_events_person_id', 'timeline_events', ['person_id'], unique=False)
    op.create_index('ix_timeline_events_evidence_id', 'timeline_events', ['evidence_id'], unique=False)

    # 14. dossiers
    op.create_table(
        'dossiers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('research_job_id', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='published', nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('dossier_content', sa.JSON(), nullable=True),
        sa.Column('source_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('evidence_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('completeness_score', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['research_job_id'], ['research_jobs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_dossiers_person_id', 'dossiers', ['person_id'], unique=False)

    # 15. topics
    op.create_table(
        'topics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_topics_name', 'topics', ['name'], unique=True)

    # 16. organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('org_type', sa.String(length=100), nullable=True),
        sa.Column('jurisdiction', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_organizations_name', 'organizations', ['name'], unique=True)

    # 17. affiliations
    op.create_table(
        'affiliations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=255), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_affiliations_person_id', 'affiliations', ['person_id'], unique=False)

    # 18. analysis_runs
    op.create_table(
        'analysis_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('analysis_type', sa.String(length=100), nullable=False),
        sa.Column('result_payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analysis_runs_person_id', 'analysis_runs', ['person_id'], unique=False)

    # 19. evidence_links
    op.create_table(
        'evidence_links',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_evidence_id', sa.Integer(), nullable=False),
        sa.Column('target_evidence_id', sa.Integer(), nullable=False),
        sa.Column('link_type', sa.String(length=100), nullable=False),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_evidence_id'], ['evidence.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_evidence_id'], ['evidence.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_evidence_links_source_target', 'evidence_links', ['source_evidence_id', 'target_evidence_id'], unique=False)

    # 20. research_snapshots
    op.create_table(
        'research_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('research_job_id', sa.Integer(), nullable=False),
        sa.Column('stage_name', sa.String(length=100), nullable=False),
        sa.Column('snapshot_data', sa.JSON(), nullable=True),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['research_job_id'], ['research_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_research_snapshots_job_id', 'research_snapshots', ['research_job_id'], unique=False)


def downgrade() -> None:
    op.drop_table('research_snapshots')
    op.drop_table('evidence_links')
    op.drop_table('analysis_runs')
    op.drop_table('affiliations')
    op.drop_table('organizations')
    op.drop_table('topics')
    op.drop_table('dossiers')
    op.drop_table('timeline_events')
    op.drop_table('initiatives')
    op.drop_table('statements')
    op.drop_table('claims')
    op.drop_table('evidence')
    op.drop_table('source_captures')
    op.drop_table('research_results')
    op.drop_table('sources')
    op.drop_table('research_queries')
    op.drop_table('research_events')
    op.drop_table('research_jobs')
    op.drop_table('persons')
    op.drop_table('users')
