from sqlalchemy import create_engine, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session


Base = declarative_base()


class Card(Base):
    __tablename__ = "cards"
    card_id = Column(Integer, primary_key=True)
    prompt = Column(String, nullable=False)
    answer = Column(String, nullable=False)


class Rating(Base):
    __tablename__ = "ratings"
    rating_id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey("cards.card_id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    rating = Column(Integer, nullable=False)


def setup_database(url: str) -> None:
    engine = create_engine(url, echo=False, future=True)
    Base.metadata.create_all(engine)


def get_session_maker(url: str) -> sessionmaker[Session]:
    engine = create_engine(url, echo=False, future=True)
    return sessionmaker(bind=engine, future=True)
