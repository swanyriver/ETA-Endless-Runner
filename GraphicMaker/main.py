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
import webapp2
import json

class MainHandler(webapp2.RequestHandler):
    def get(self):
        with open('generator.html', 'r') as outputFile:
            self.response.write(outputFile.read())
            return

    #create graphics JSON from form data
    kDRAWING = "drawings"
    kDEADLY = "deadly"
    def post(self):

        #self.response.write(json.dumps(self.request.POST, indent=2))
        #self.response.write(str(self.request.POST.getall('drawing')))

        outputDict = {}
        if self.kDEADLY in self.request.POST:
            outputDict["deadly"] = True
        drawings = [d.splitlines() for d in self.request.POST.getall(self.kDRAWING) if d]

        if drawings:
            outputDict[self.kDRAWING] = drawings
            self.response.headers['Content-Type'] = "application/json"
            self.response.write(json.dumps(outputDict, indent=2))
        else:
            self.response.headers['Content-Type'] = "text/plain"
            self.response.write("Error: drawing must have at least one frame with at least one character")
        return

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
