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

    @staticmethod
    def uniformDrawing(drawing):
        # NOTE: this algorithm creates a drawing of uniformly lengthed strings by
        # removing all right padding
        # remove all-whitespace lines at beginning and end of drawing
        # then add back right padding up to the longest(s)(non-whitespace-to-not-whitespace) strings in the drawing
        # remove unnecessary left padding (at least one string will have a non whitespace char in index 0)

        drawing = [line.rstrip() for line in drawing]

        while drawing and not drawing[0]:
            del drawing[0]
        while drawing and not drawing[-1]:
            del drawing[-1]

        # return early if all lines were whitespace
        if not drawing: return drawing

        maxLength = max(len(line) for line in drawing)
        drawing = [line + (" " * (maxLength - len(line))) for line in drawing]

        leftRemove = 0
        while leftRemove < min(len(line) for line in drawing):
            if not all(line[leftRemove] == " " for line in drawing): break
            leftRemove += 1
        drawing = [line[leftRemove:] for line in drawing]

        return drawing

    # create graphics JSON from form data
    def post(self):
        kDRAWING = "drawings"
        kDEADLY = "deadly"

        outputDict = {}
        outputDict[kDEADLY] = (kDEADLY in self.request.POST)

        #uniform pad nonEmpty frames
        drawings = [MainHandler.uniformDrawing(d.splitlines()) for d in self.request.POST.getall(kDRAWING) if d]
        #remove empty frames
        drawings = filter(None, drawings)


        #todo render json in html with option to return to editing including extra frames
        #todo run parse tests on server and display error/success
        #todo show game rendering of graphic  (is this even possible??)
        if drawings:
            outputDict[kDRAWING] = drawings
            self.response.headers['Content-Type'] = "application/json"
            self.response.write(json.dumps(outputDict, indent=2))
        else:
            self.response.headers['Content-Type'] = "text/plain"
            self.response.write("Error: drawing must have at least one frame with at least one character")
        return

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
