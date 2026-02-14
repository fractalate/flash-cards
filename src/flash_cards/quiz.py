import os

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
    card = (
        session.query(Card)
        .limit(1)
    ).first()
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


def main(argv: list[str]):
    ensure_database()
    Session = get_session_maker(DATABASE_URL)

    while True:
        with Session() as session:
            card = get_next_card(session)
            
            if not card:
                print("no more cards")
                break

            input(card.prompt + " [press return to reveal]")
            print(card.answer)

            rating = collect_rating()

            store_rating(session, card, rating)

if __name__ == "__main__":
    import sys
    main(sys.argv)
