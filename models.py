from typing import Optional
import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, LargeBinary, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import NullType

class Base(DeclarativeBase):
    pass


class Belts(Base):
    __tablename__ = 'belts'
    __table_args__ = (
        Index('belts_beltTitle_IDX', 'beltTitle', unique=True),
    )

    beltId: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    beltTitle: Mapped[Optional[str]] = mapped_column(Text)
    stripeTitle: Mapped[Optional[str]] = mapped_column(Text)
    classCount: Mapped[Optional[int]] = mapped_column(Integer)
    imageSource: Mapped[Optional[str]] = mapped_column(Text)
    stripeCount: Mapped[Optional[int]] = mapped_column(Integer)

    requirements: Mapped[list['Requirements']] = relationship('Requirements', back_populates='belts')

class Requirements(Base):
    __tablename__ = 'requirements'
    __table_args__ = (
        Index('requirements_stripeTitle_IDX', 'stripeTitle', unique=True),
    )

    requirementId: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    beltId: Mapped[Optional[int]] = mapped_column(ForeignKey('belts.beltId'))
    stripeTitle: Mapped[Optional[str]] = mapped_column(Text)
    requiredClasses: Mapped[Optional[int]] = mapped_column(Integer)

    belts: Mapped[Optional['Belts']] = relationship('Belts', back_populates='requirements')

class Promotions(Base):
    __tablename__ = 'promotions'
    __table_args__ = (
        Index('idx_promotions_n1', 'badgeNumber'),
        Index('promitions_pk', 'promotionId', unique=True)
    )

    promotionId: Mapped[int] = mapped_column(Integer, primary_key=True)
    badgeNumber: Mapped[int] = mapped_column(Integer, nullable=False)
    beltId: Mapped[Optional[int]] = mapped_column(Integer)
    beltTitle: Mapped[Optional[str]] = mapped_column(Text)
    stripeId: Mapped[Optional[int]] = mapped_column(Integer)
    stripeTitle: Mapped[Optional[str]] = mapped_column(Text)
    studentName: Mapped[Optional[str]] = mapped_column(Text)
    promotionDate: Mapped[Optional[str]] = mapped_column(Text)
    studentFirstName: Mapped[Optional[str]] = mapped_column(Text)
    studentLastName: Mapped[Optional[str]] = mapped_column(Text)
    comments: Mapped[Optional[str]] = mapped_column(Text)


class Stripes(Base):
    __tablename__ = 'stripes'

    stripeName: Mapped[str] = mapped_column(Text, nullable=False)
    rankNum: Mapped[int] = mapped_column(ForeignKey('ranks.rankNum'), nullable=False)
    stripeId: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    classCount: Mapped[Optional[int]] = mapped_column(Integer)
    seqNum: Mapped[Optional[int]] = mapped_column(Integer)

    #ranks: Mapped['Ranks'] = relationship('Ranks', back_populates='stripes')

class Students(Base):
    __tablename__ = 'students'

    badgeNumber: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstName: Mapped[Optional[str]] = mapped_column(Text)
    lastName: Mapped[Optional[str]] = mapped_column(Text)
    namePrefix: Mapped[Optional[str]] = mapped_column(Text)
    email: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(Text)
    address2: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(Text)
    country: Mapped[Optional[str]] = mapped_column(Text)
    state: Mapped[Optional[str]] = mapped_column(Text)
    zip: Mapped[Optional[str]] = mapped_column(Text)
    birthDate: Mapped[Optional[str]] = mapped_column(Text)
    phoneHome: Mapped[Optional[str]] = mapped_column(Text)
    phoneMobile: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(Text)
    memberSince: Mapped[Optional[str]] = mapped_column(Text)
    gender: Mapped[Optional[str]] = mapped_column(Text)
    ethnicity: Mapped[Optional[str]] = mapped_column(Text)
    studentImageBytes: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    studentImagePath: Mapped[Optional[str]] = mapped_column(Text)
    studentImageBase64: Mapped[Optional[str]] = mapped_column(Text)
    middleName: Mapped[Optional[str]] = mapped_column(Text)
    studentImageName: Mapped[Optional[str]] = mapped_column(Text)
    studentImageType: Mapped[Optional[str]] = mapped_column(Text)
    currentRankNum: Mapped[Optional[int]] = mapped_column(Integer)
    currentRankName: Mapped[Optional[str]] = mapped_column(Text)
    currentStripeId: Mapped[Optional[int]] = mapped_column(Integer)
    currentStripeName: Mapped[Optional[str]] = mapped_column(Text)

class Classes(Base):
    __tablename__ = 'classes'

    classNum: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    className: Mapped[Optional[str]] = mapped_column(Text)
    styleNum: Mapped[Optional[int]] = mapped_column(Integer)
    styleName: Mapped[Optional[str]] = mapped_column(Text)
    classDayOfWeek: Mapped[Optional[int]] = mapped_column(Integer)
    classStartTime: Mapped[Optional[str]] = mapped_column(Text)
    classFinisTime: Mapped[Optional[str]] = mapped_column(Text)
    classDuration: Mapped[Optional[int]] = mapped_column(Integer)
    allowedRanks: Mapped[Optional[str]] = mapped_column(Text)
    classDisplayTitle: Mapped[Optional[int]] = mapped_column(Integer)
    allowedAges: Mapped[Optional[str]] = mapped_column(Text)
    classCheckinStart: Mapped[Optional[str]] = mapped_column(Text)
    classCheckInFinis: Mapped[Optional[str]] = mapped_column(Text)
    isPromotions: Mapped[Optional[str]] = mapped_column(Text(1))

class Attendance(Base):
    __tablename__ = 'attendance'
    __table_args__ = (
        Index('attendanceBadgeNumber', 'badgeNumber'),
    )

    attendance_id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    badgeNumber: Mapped[Optional[int]] = mapped_column(Integer)
    checkinDateTime: Mapped[Optional[str]] = mapped_column(Text)
    checkinDate: Mapped[Optional[str]] = mapped_column(Text)
    checkinTime: Mapped[Optional[str]] = mapped_column(Text)
    studentFirstName: Mapped[Optional[str]] = mapped_column(Text)
    studentLastName: Mapped[Optional[str]] = mapped_column(Text)
    studentStatus: Mapped[Optional[str]] = mapped_column(Text)
    studentRankNum: Mapped[Optional[int]] = mapped_column(Integer)
    studentRankName: Mapped[Optional[str]] = mapped_column(Text)
    studentStripeId: Mapped[Optional[int]] = mapped_column(Integer)
    studentStripeName: Mapped[Optional[str]] = mapped_column(Text)
    classNum: Mapped[Optional[int]] = mapped_column(Integer)
    className: Mapped[Optional[str]] = mapped_column(Text)
    classStartTime: Mapped[Optional[str]] = mapped_column(Text)
    styleNum: Mapped[Optional[int]] = mapped_column(Integer)
    appliesPromotion: Mapped[Optional[str]] = mapped_column(Text)

class ElgibilityCounts(Base):
    __tablename__ = 'elgibilityCounts'
    __table_args__ = (
        Index('elgibilityCounts_n1', 'eligibleCount'),
    )

    rowNum: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    beltId: Mapped[Optional[int]] = mapped_column(Integer)
    stripePrefixSeq: Mapped[Optional[int]] = mapped_column(Integer)
    beltTitle: Mapped[Optional[str]] = mapped_column(Text)
    stripeTitle: Mapped[Optional[str]] = mapped_column(Text)
    classCount: Mapped[Optional[int]] = mapped_column(Integer)
    eligibleCount: Mapped[Optional[int]] = mapped_column(Integer)

class VwEligibilityCounts(Base):
    __tablename__ = 'vw_elgibility_counts'      # Name of the view in SQLite
    rowNum = Column(Integer, primary_key=True)  # Map an existing unique column
    beltId = Column(Integer)
    stripePrefixSeq = Column(Integer)
    beltTitle       = Column(Text)
    stripeTitle     = Column(Text)
    classCount      = Column(Integer)
    eligibleCount   = Column(Integer)

# vwEligibilityCounts = Table(
#     'vw_elgibility_counts', Base.metadata,
#     Column('rowNum', NullType),
#     Column('beltId', Integer),
#     Column('stripePrefixSeq', Integer),
#     Column('beltTitle', Text),
#     Column('stripeTitle', NullType),
#     Column('classCount', Integer),
#     Column('eligibleCount', NullType)
# )
