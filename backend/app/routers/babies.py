from datetime import UTC, datetime

from fastapi import APIRouter, status
from sqlalchemy import select

from app.deps import AccessibleBaby, CurrentUser, DbSession
from app.models import Baby, Caregiving, CaregivingRole
from app.schemas.baby import BabyCreate, BabyRead

router = APIRouter(prefix="/babies", tags=["babies"])


@router.get("", response_model=list[BabyRead])
def list_babies(db: DbSession, user: CurrentUser) -> list[Baby]:
    query = (
        select(Baby)
        .join(Caregiving)
        .where(Caregiving.user_id == user.id, Caregiving.accepted_at.is_not(None))
        .order_by(Baby.birth_date.desc())
    )
    return list(db.scalars(query))


@router.post("", response_model=BabyRead, status_code=status.HTTP_201_CREATED)
def create_baby(body: BabyCreate, db: DbSession, user: CurrentUser) -> Baby:
    # **body.model_dump() unpacks the dict into keyword args: Baby(name=..., birth_date=...)
    baby = Baby(**body.model_dump())
    now = datetime.now(UTC)
    # Whoever adds the baby owns it, and has implicitly accepted.
    baby.caregivings.append(
        Caregiving(user=user, role=CaregivingRole.OWNER, invited_at=now, accepted_at=now)
    )
    db.add(baby)
    db.commit()
    return baby


@router.get("/{baby_id}", response_model=BabyRead)
def get_baby(baby: AccessibleBaby) -> Baby:
    return baby
