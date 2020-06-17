from pecan import expose, redirect, abort
from webob.exc import status_map
from urlwatch_api import model

import tempfile
import subprocess

class CheckController(object):
    def __init__(self, row):
        for c in ['id', 'guid', 'data', 'data_unfiltered', 'tries', 'etag',
                  'error', 'proxy']:
            setattr(self, c, getattr(row, c))
        for c in ['timestamp']:
            v = getattr(row, c)
            setattr(self, c, int(v.timestamp()) if v else None)

    @expose('json')
    def index(self):
        return self.__dict__

    # ick, can't use 'data' here because of existing element
    @expose(route='get-data-filtered')
    def get_data(self):
        for row in model.Session.query(model.Blob).filter_by(guid=self.data):
            return row.data

    @expose(route='get-data-unfiltered')
    def get_data_unfiltered(self):
        for row in model.Session.query(model.Blob).filter_by(guid=self.data_unfiltered):
            return row.data

class SiteController(object):
    def __init__(self, row):
        for c in ['guid', 'name', 'url',
                  'uptime_hour', 'uptime_day', 'uptime_week', 'uptime_30',
                  'uptime_90']:
            setattr(self, c, getattr(row, c))
        for c in ['last_change', 'last_up', 'last_down', 'last_check']:
            v = getattr(row, c)
            setattr(self, c, int(v.timestamp()) if v else None)
            
    @expose('json')
    def index(self):
        return self.__dict__

    @expose('json')
    def checks(self):
        r = []
        for row in model.Session.query(model.SiteCheck).filter_by(guid=self.guid):
            c = CheckController(row)
            r.append(c.__dict__)
        return r

    @expose('json')
    def downtime(self):
        r = []
        start = None
        error = None
        for row in model.Session.query(model.SiteCheck).filter_by(guid=self.guid).order_by(model.SiteCheck.timestamp):
            c = CheckController(row)
            if c.tries > 0:
                if start is None:
                    start = c.timestamp
                    error = c.error
            else:
                if start:
                    r.append({
                        'start': start,
                        'end': c.timestamp,
                        'duration': c.timestamp - start,
                        'error': error,
                    })
                    start = None
        return r

    @expose('json', route='get-changes-filtered')
    def get_changes_filtered(self):
        r = []
        last = None
        for row in model.Session.query(model.SiteCheck).filter_by(guid=self.guid).order_by(model.SiteCheck.timestamp):
            if row.data is None:
                continue
            if last is None or last != row.data:
                r.append(CheckController(row).__dict__)
            last = row.data
        return r
   
    @expose('json', route='get-changes-unfiltered')
    def get_changes_unfiltered(self):
        r = []
        last = None
        for row in model.Session.query(model.SiteCheck).filter_by(guid=self.guid).order_by(model.SiteCheck.timestamp):
            if row.data_unfiltered is None:
                continue
            if last is None or last != row.data_unfiltered:
                r.append(CheckController(row).__dict__)
            last = row.data_unfiltered
        return r
   
    @expose('json')
    def _lookup(self, id_, *remainder):
        for row in model.Session.query(model.SiteCheck).filter_by(id=id_):
            return CheckController(row), remainder
            
        abort(404)
    

class SitesController(object):
    @expose('json')
    def index(self):
        r = []
        for row in model.Session.query(model.Site).all():
            site = SiteController(row)
            r.append(site.__dict__)
        return {'sites': r}

    @expose()
    def _lookup(self, guid, *remainder):
        for row in model.Session.query(model.Site).filter_by(guid=guid):
            return SiteController(row), remainder
            
        abort(404)

class APIController(object):
    @expose()
    def index(self):
        return 'hi'

    sites = SitesController()

    @expose(content_type='text/plain')
    def blob(self, guid):
        for row in model.Session.query(model.Blob).filter_by(guid=guid):
            return row.data
            
        abort(404)


    @expose(content_type='text/plain', route='blob-diff')
    def blob_diff(self, a, b):
        for row in model.Session.query(model.Blob).filter_by(guid=a):
            adata = row.data
            break
        for row in model.Session.query(model.Blob).filter_by(guid=b):
            bdata = row.data
            break

        print('%d %d' % (len(adata), len(bdata)))

        af = tempfile.NamedTemporaryFile(mode='w')
        af.write(adata)
        af.flush()
        bf = tempfile.NamedTemporaryFile(mode='w')
        bf.write(bdata)
        bf.flush()

        cmd = ['diff', '-u', af.name, bf.name]
        out = subprocess.run(cmd, check=False, stdout=subprocess.PIPE).stdout
        print('%d' % len(out))
        return out

