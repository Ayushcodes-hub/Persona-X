from engine.analysis.topic_extractor import TopicExtractor
from engine.analysis.topic_schemas import (
    TopicExtractionResult,
)
from engine.analysis.topic_view_service import (
    TopicViewExtractionService,
)
from engine.analysis.view_extractor import ViewExtractor


def test_topic_extractor_detects_healthcare():
    extractor = TopicExtractor()

    result = extractor.extract(
        "The interview discussed healthcare reform and hospital access."
    )

    assert isinstance(result, TopicExtractionResult)
    assert result.topic_count >= 1

    topics = [topic.topic for topic in result.topics]

    assert "healthcare" in topics


def test_topic_extractor_detects_multiple_topics():
    extractor = TopicExtractor()

    result = extractor.extract(
        "The discussion covered healthcare, education, "
        "taxation and climate policy."
    )

    topics = {topic.topic for topic in result.topics}

    assert "healthcare" in topics
    assert "education_policy" in topics
    assert "taxation" in topics
    assert "environment" in topics


def test_topic_extractor_deduplicates_topic_matches():
    extractor = TopicExtractor()

    result = extractor.extract(
        "Healthcare access requires better healthcare funding "
        "and healthcare infrastructure."
    )

    healthcare_topics = [
        topic
        for topic in result.topics
        if topic.topic == "healthcare"
    ]

    assert len(healthcare_topics) == 1


def test_topic_extractor_empty_text_returns_empty_result():
    extractor = TopicExtractor()

    result = extractor.extract("")

    assert result.topic_count == 0
    assert result.view_count == 0


def test_topic_confidence_represents_extraction_not_truth():
    extractor = TopicExtractor()

    result = extractor.extract(
        "The person discussed healthcare policy."
    )

    topic = next(
        topic
        for topic in result.topics
        if topic.topic == "healthcare"
    )

    assert 0.0 <= topic.confidence <= 1.0
    assert topic.extraction_method == "deterministic_keyword"


def test_view_extractor_detects_support():
    extractor = ViewExtractor()

    views = extractor.extract(
        "I strongly support expanding healthcare access.",
        topic="healthcare",
    )

    assert len(views) == 1
    assert views[0].position_type == "support"
    assert views[0].position == "supportive"
    assert views[0].topic == "healthcare"


def test_view_extractor_detects_opposition():
    extractor = ViewExtractor()

    views = extractor.extract(
        "I oppose this immigration policy.",
        topic="immigration",
    )

    assert len(views) == 1
    assert views[0].position_type == "oppose"
    assert views[0].position == "opposed"


def test_topic_mention_alone_does_not_create_view():
    extractor = ViewExtractor()

    views = extractor.extract(
        "The interview discussed healthcare policy.",
        topic="healthcare",
    )

    assert views == []


def test_view_extractor_preserves_attribution_status():
    extractor = ViewExtractor()

    views = extractor.extract(
        "I support renewable energy.",
        topic="energy",
        attribution_status="direct_quote",
    )

    assert len(views) == 1
    assert views[0].attribution_status == "direct_quote"


def test_combined_service_extracts_topic_and_view():
    service = TopicViewExtractionService()

    result = service.extract(
        "I strongly support expanding healthcare access.",
        context="interview",
        attribution_status="direct_quote",
    )

    assert result.topic_count >= 1
    assert result.view_count >= 1

    healthcare = next(
        topic
        for topic in result.topics
        if topic.topic == "healthcare"
    )

    assert healthcare.context == "interview"

    view = next(
        view
        for view in result.views
        if view.topic == "healthcare"
    )

    assert view.position == "supportive"
    assert view.attribution_status == "direct_quote"


def test_combined_service_does_not_create_view_without_position():
    service = TopicViewExtractionService()

    result = service.extract(
        "The person discussed healthcare and education.",
        context="interview",
    )

    assert result.topic_count >= 2
    assert result.view_count == 0


def test_professional_topic_is_not_automatically_political():
    service = TopicViewExtractionService()

    result = service.extract(
        "The athlete discussed training, fitness and injury recovery."
    )

    topics = {topic.topic for topic in result.topics}

    assert "training" in topics
    assert "injury" in topics

    assert all(
        topic.topic not in {
            "political_orientation",
            "left",
            "right",
            "liberal",
            "conservative",
        }
        for topic in result.topics
    )


def test_view_extraction_does_not_assign_ideology():
    service = TopicViewExtractionService()

    result = service.extract(
        "I strongly support expanding renewable energy."
    )

    assert result.view_count >= 1

    for view in result.views:
        assert not hasattr(view, "ideology")
        assert view.position in {
            "supportive",
            "opposed",
            "belief_expressed",
            None,
        }