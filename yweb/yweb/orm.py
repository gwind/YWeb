#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

import yweb.utils.db
from yweb.exceptions import YwebDBError

ORMBase = declarative_base()


def get_db_session():

    DB_URI = yweb.utils.db.get_db_uri()
    dbengine = create_engine(DB_URI, echo=False)
    session_factory = sessionmaker(bind=dbengine)
    Session = scoped_session(session_factory)

    return Session


def create_all(echo=False):

    DB_URI = yweb.utils.db.get_db_uri()
    dbengine = create_engine(DB_URI, echo=echo)
    ORMBase.metadata.create_all(dbengine)


def drop_all(echo=False):

    DB_URI = yweb.utils.db.get_db_uri()
    dbengine = create_engine(DB_URI, echo=echo)
    ORMBase.metadata.drop_all(dbengine)


