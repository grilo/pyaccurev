#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import accurev.element


class TestAccuRevElement(unittest.TestCase):

    def test_element_from_stat(self):
	xml = """<?xml version="1.0" encoding="utf-8"?>
	    <AcResponse
		Command="stat"
		Directory="/jenkins/home/jenkins/pruebas/joaogn/pyacc"
		TaskId="302012">
	      <element
		  location="/./ITQA"
		  dir="yes"
		  executable="no"
		  id="138803"
		  elemType="dir"
		  modTime="0"
		  hierType="parallel"
		  Virtual="2094/1"
		  namedVersion="ING_PRO_ITQA/1"
		  Real="32/1"
		  status="(backed)"/>
	    </AcResponse>"""

	element = list(accurev.element.Element.from_stat(None, xml))[0]
        for key in ['location', 'eid', 'real_version']:
            out = getattr(element, key)
            self.assertTrue(isinstance(out, str))

    def test_element_from_cpkdescribe(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <acResponse>
              <issues>
                <issue>
                  <issueNum>100</issueNum>
                  <elements>
                    <element
                        id="10"
                        real_version="22545/1"
                        basis_version="21580/1"
                        location="/path/to/element.py"
                        dir="no"
                        elemType="text"
                        missing="false"/>
                    <element
                        id="1010"
                        real_version="22545/3"
                        basis_version="22545/2"
                        location="/path/to/another/element.py"
                        dir="no"
                        elemType="text"
                        missing="false"/>
                  </elements>
                </issue>
                <issue>
                  <issueNum>200</issueNum>
                  <elements>
                    <element
                        id="20"
                        real_version="22545/1"
                        basis_version="21580/1"
                        location="/path/to/element.py"
                        dir="no"
                        elemType="text"
                        missing="false"/>
                    <element
                        id="2020"
                        real_version="22545/3"
                        basis_version="22545/2"
                        location="/path/to/another/element.py"
                        dir="no"
                        elemType="text"
                        missing="false"/>
                  </elements>
                </issue>
              </issues>
            </acResponse>"""

	issue_elements = accurev.element.Element.from_cpkdescribe(None, xml)
        self.assertTrue(isinstance(issue_elements, dict))
        self.assertTrue(len(issue_elements.keys()), 2)
        self.assertTrue(len(issue_elements['100'].keys()), 2)
        self.assertTrue(len(issue_elements['100'].values()), 2)
        for element in issue_elements['100'].values():
            for key in ['location', 'eid', 'real_version', 'missing']:
                out = getattr(element, key)
                self.assertTrue(isinstance(out, str))

    def test_element_preserves_backslash_path(self):
	element = accurev.element.Element(None, location='\\.\\some\\element\\path')
        self.assertEqual(element.location, '\\.\\some\\element\\path')

    def test_element_normalizes_forwardslash_path(self):
	element = accurev.element.Element(None, location='/some/element/path')
        self.assertEqual(element.location, '\\.\\some\\element\\path')
