import os

from sqlalchemy import func, case, literal, or_
from sqlalchemy.orm import Session

from flash_cards.database import (
    Card,
    Rating,
    get_session_maker,
    setup_database,
)


DATABASE_NAME = "flash_cards.db"
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"  # XXX what's a good way to take any file path and turn it into a url?


def ensure_database() -> None:
    try:
        os.stat(DATABASE_NAME)
    except FileNotFoundError:
        setup_database(DATABASE_URL)


def get_next_card(session: Session) -> None | Card:
    adjusted_ratings_cte = (
        session.query(
            Rating,
            func.avg(Rating.rating).over(
                partition_by=Rating.card_id,
                order_by=Rating.created_at.desc(),
                rows=(-10, 0),
            ).label("average_rating"),
            func.row_number().over(
                partition_by=Rating.card_id,
                order_by=Rating.created_at.desc(),
            ).label("card_rating_number"),
            func.datetime(
                Rating.created_at,
                case(
                    (Rating.rating == literal(1), literal("+0 minutes")),
                    (Rating.rating == literal(2), literal("+5 minutes")),
                    (Rating.rating == literal(3), literal("+30 minutes")),
                    (Rating.rating == literal(4), literal("+24 hours")),
                    else_=literal("+0 minutes"),
                ),
            ).label("due_at"),
        )
    ).cte("adjusted_ratings_cte")

    card_query = (
        session.query(Card)
        .outerjoin(
            adjusted_ratings_cte,
            Card.card_id == adjusted_ratings_cte.c.card_id,
        )
        .where(
            or_(
                adjusted_ratings_cte.c.card_rating_number.is_(None),
                adjusted_ratings_cte.c.card_rating_number == literal(1),
            )
        )
        .order_by(
            adjusted_ratings_cte.c.due_at.asc().nulls_first(),
            adjusted_ratings_cte.c.average_rating,
        )
    )

    card = card_query.first()

    return card


def collect_rating() -> int:
    rating = None
    while rating is None:
        rating = input("rating [1-4]: ")
        if rating not in ("1", "2", "3", "4"):
            rating = None
    return int(rating)


def store_rating(session: Session, card: Card, rating: int) -> None:
    session.add(Rating(
        card_id=card.card_id,
        rating=rating,
    ))
    session.commit()


def main(argv: list[str]) -> None:
    ensure_database()
    Session = get_session_maker(DATABASE_URL)

    while True:
        with Session() as session:
            card = get_next_card(session)
            
            if not card:
                print("no more cards")
                break

            print()
            print(card.prompt)
            print()
            input("[press return to reveal]")
            print()
            print(card.answer)
            print()

            rating = collect_rating()
            store_rating(session, card, rating)

            print()


if __name__ == "__main__":
    import sys
    main(sys.argv)
