"""
ResearchPilot AI - Database Models (SQLAlchemy)
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime,
    ForeignKey, Table, JSON
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Association tables
paper_authors = Table(
    "paper_authors",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)

paper_topics = Table(
    "paper_topics",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id"), primary_key=True),
)

paper_citations = Table(
    "paper_citations",
    Base.metadata,
    Column("citing_paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
    Column("cited_paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    queries = relationship("ResearchQuery", back_populates="user")


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    affiliation = Column(String(500), nullable=True)
    papers = relationship("Paper", secondary=paper_authors, back_populates="authors")


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    category = Column(String(100), nullable=True)
    papers = relationship("Paper", secondary=paper_topics, back_populates="topics")


class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(1000), index=True)
    abstract = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    doi = Column(String(500), nullable=True, unique=True)
    url = Column(String(1000), nullable=True)
    source = Column(String(100), nullable=True)  # arxiv, semantic_scholar, etc.
    source_id = Column(String(500), nullable=True)
    citation_count = Column(Integer, default=0)
    keywords = Column(JSON, nullable=True)
    research_field = Column(String(255), nullable=True)
    pdf_url = Column(String(1000), nullable=True)
    journal = Column(String(500), nullable=True)
    venue = Column(String(500), nullable=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    authors = relationship("Author", secondary=paper_authors, back_populates="papers")
    topics = relationship("Topic", secondary=paper_topics, back_populates="papers")
    analysis = relationship("PaperAnalysis", back_populates="paper", uselist=False)
    citations_given = relationship(
        "Paper", secondary=paper_citations,
        primaryjoin="Paper.id == paper_citations.c.citing_paper_id",
        secondaryjoin="Paper.id == paper_citations.c.cited_paper_id",
        backref="cited_by"
    )


class PaperAnalysis(Base):
    __tablename__ = "paper_analyses"
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), unique=True)
    problem_statement = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    dataset = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    key_findings = Column(Text, nullable=True)
    future_work = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    raw_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    paper = relationship("Paper", back_populates="analysis")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500))
    file_type = Column(String(50))
    file_path = Column(String(1000))
    file_size = Column(Integer)
    extracted_text = Column(Text, nullable=True)
    detected_title = Column(String(1000), nullable=True)
    detected_authors = Column(JSON, nullable=True)
    detected_abstract = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    is_indexed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResearchQuery(Base):
    __tablename__ = "research_queries"
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    research_plan = Column(JSON, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="queries")
    results = relationship("ResearchResult", back_populates="query")


class ResearchResult(Base):
    __tablename__ = "research_results"
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("research_queries.id"))
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)
    relevance_score = Column(Float, default=0.0)
    rank = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    query = relationship("ResearchQuery", back_populates="results")
    paper = relationship("Paper")


class ResearchGap(Base):
    __tablename__ = "research_gaps"
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("research_queries.id"), nullable=True)
    gap_description = Column(Text)
    evidence = Column(Text, nullable=True)
    importance = Column(String(50), default="medium")
    possible_research_questions = Column(JSON, nullable=True)
    supporting_papers = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResearchRecommendation(Base):
    __tablename__ = "research_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("research_queries.id"), nullable=True)
    research_idea = Column(Text)
    why_it_matters = Column(Text, nullable=True)
    existing_evidence = Column(Text, nullable=True)
    research_gap = Column(Text, nullable=True)
    suggested_methodology = Column(Text, nullable=True)
    possible_dataset = Column(Text, nullable=True)
    expected_contribution = Column(Text, nullable=True)
    difficulty_level = Column(String(50), default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)


class LiteratureReview(Base):
    __tablename__ = "literature_reviews"
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("research_queries.id"), nullable=True)
    title = Column(String(1000), nullable=True)
    introduction = Column(Text, nullable=True)
    existing_research = Column(Text, nullable=True)
    major_approaches = Column(Text, nullable=True)
    comparison_of_methods = Column(Text, nullable=True)
    important_findings = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    research_gaps = Column(Text, nullable=True)
    emerging_trends = Column(Text, nullable=True)
    future_directions = Column(Text, nullable=True)
    references = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
