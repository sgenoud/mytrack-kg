#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import os
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
import datetime
import gviz_api
import logging

class WeightPoint(db.Model):
    user = db.UserProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    weight = db.FloatProperty()

def _build_js(query_result):
    description = {"date": ("datetime", "Date"),
                    "weight": ("number", "Weight in Kg")}
    data = [{"weight": 80, "date": datetime.datetime(2011, 12, 1)},
            {"weight": 81, "date": datetime.datetime(2011, 12, 2)},
            {"weight": 82, "date": datetime.datetime(2011, 12, 3)},
            {"weight": 83, "date": datetime.datetime(2011, 12, 4)},
            {"weight": 84, "date": datetime.datetime(2011, 12, 5)},]
    for point in query_result:
        logging.info(point.weight)
        data.append(dict(weight=point.weight, date=point.date))


    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    # Creating a JavaScript code string
    jscode = data_table.ToJSCode("jscode_data",
                                columns_order=("date", "weight"),
                                order_by="date")
    return jscode

class MainPage(webapp.RequestHandler):
    def get(self):
        guestbook_name=self.request.get('guestbook_name')

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            is_user = True

            q = WeightPoint.all().filter('user = ', users.get_current_user())
            jscode = _build_js(q.fetch(356))

        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            is_user = False

        template_values = {
            'url': url,
            'url_linktext': url_linktext,
            'is_user': is_user,
            'jscode': jscode

        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        user = users.get_current_user()
        if user:
            weight = self.request.get('weight')
            weight_point = WeightPoint(weight=float(weight), user=user)
            weight_point.put()
            self.redirect('/')



def main():
    application = webapp.WSGIApplication([('/', MainPage)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
