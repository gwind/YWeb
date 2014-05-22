#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from yweb.conf import settings

ORMBase = declarative_base()


def get_db_session():

    dbengine = create_engine(settings.DB_URI, echo=False)
    session_factory = sessionmaker(bind=dbengine)
    Session = scoped_session(session_factory)

    return Session


def create_all(echo=False):

    dbengine = create_engine(settings.DB_URI, echo=echo)
    ORMBase.metadata.create_all(dbengine)


def drop_all(echo=False):

    dbengine = create_engine(settings.DB_URI, echo=echo)
    ORMBase.metadata.drop_all(dbengine)

