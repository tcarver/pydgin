''' Test for LD rest interface. '''
from django.test import TestCase
from rest_framework import status
from django.core.urlresolvers import reverse
import json


class LDRestTest(TestCase):

    def test_ld_list(self):
        ''' Test retrieving markers in LD of given marker. '''
        url = reverse('rest:ld-list') + "?format=json&m1=rs10774624"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ld = json.loads(response.content.decode("utf-8"))[0]['ld']
        self.assertGreater(len(ld), 0, 'results found')
