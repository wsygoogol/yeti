from __future__ import unicode_literals
import time

from flask_classy import route
from bson.json_util import loads
from flask import request

from core.web.api.crud import CrudSearchApi, CrudApi
from core import database
from core.web.api.api import render
from core.helpers import iterify
from core.investigation import Investigation


class LinkSearch(CrudSearchApi):
    objectmanager = database.Link


class Link(CrudApi):
    objectmanager = database.Link

    def delete(self, id):
        """Deletes the corresponding entry from the database

        :query ObjectID id: Element ID
        :>json string deleted: The deleted element's ObjectID
        """
        obj = self.objectmanager.objects.get(id=id)
        obj.delete()
        Investigation.objects(links__id=id).update(set__links__S__id="local-{}".format(time.time()))
        return render({"deleted": id})

    @route("/multidelete", methods=['POST'])
    def multidelete(self):
        data = loads(request.data)
        ids = iterify(data['ids'])
        self.objectmanager.objects(id__in=ids).delete()
        Investigation.objects(links__id__in=ids).update(set__links__S__id="local-{}".format(time.time()))
        return render({"deleted": ids})

    @route("/multiupdate", methods=['POST'])
    def multiupdate(self):
        data = loads(request.data)
        ids = data['ids']
        new_description = data['new']['description']
        updated = []
        for link in self.objectmanager.objects(id__in=ids):
            # link.select_related() #does not work
            # must call src and dst to dereference dbrefs and not raise an exception
            link.src
            link.dst
            link.description = new_description
            link.save()
            updated.append(link.id)

        return render({"updated": updated})
