import datetime

from yweb.orm import ORMBase

from sqlalchemy import Column, Integer, String, \
    Sequence, DateTime, Table, ForeignKey, Boolean, Text

from sqlalchemy.orm import relationship, backref


class SiteConfig(ORMBase):

    ''' Global site config, k-v style'''

    __tablename__ = 'site_config'

    id = Column(Integer, Sequence('site_config_id_seq'), primary_key=True)
    key   = Column( String(256) )
    value = Column( Text )

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __unicode__(self):
        return "SiteConfig <%s>" % self.id

    @classmethod
    def get(clc, db, key, default=None, vtype=str):
        x = db.query(clc).filter_by( key = key ).first()
        if not x:
            return default

        if vtype == int:
            try:
                v = int(x.value)
            except:
                v = default
            return v
        else:
            return x.value

    @classmethod
    def set(clc, db, key, value):

        x = db.query(clc).filter_by( key = key ).first()

        if x:
            x.value = value
        else:
            x = clc(key=key, value=value)

        db.add(x)
        db.commit()

