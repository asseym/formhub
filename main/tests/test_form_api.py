from django.core.urlresolvers import reverse
from django.utils import simplejson

from test_base import MainTestCase
from main.views import api
from odk_viewer.models.parsed_instance import ParsedInstance

def dict_for_mongo_without_userform_id(parsed_instance):
    d = parsed_instance.to_dict_for_mongo()
    # remove _userform_id since its not returned by the API
    d.pop(ParsedInstance.USERFORM_ID)
    return d

class TestFormAPI(MainTestCase):

    def setUp(self):
        MainTestCase.setUp(self)
        self._create_user_and_login()
        self._publish_transportation_form_and_submit_instance()
        self.api_url = reverse(api, kwargs={
            'username': self.user.username,
            'id_string': self.xform.id_string
        })

    def test_api(self):
        # query string
        response = self.client.get(self.api_url, {})
        self.assertEqual(response.status_code, 200)
        d = dict_for_mongo_without_userform_id(self.xform.surveys.all()[0].parsed_instance)
        find_d = simplejson.loads(response.content)[0]
        self.assertEqual(sorted(find_d, key=find_d.get), sorted(d, key=d.get))

    def test_api_with_query(self):
        # query string
        json = '{"transport/available_transportation_types_to_referral_facility":"none"}'
        data = {'query': json}
        response = self.client.get(self.api_url, data)
        self.assertEqual(response.status_code, 200)
        d = dict_for_mongo_without_userform_id(self.xform.surveys.all()[0].parsed_instance)
        find_d = simplejson.loads(response.content)[0]
        self.assertEqual(sorted(find_d, key=find_d.get), sorted(d, key=d.get))

    def test_api_query_no_records(self):
        # query string
        json = '{"available_transporation_types_to_referral_facility": "bicycle"}'
        data = {'query': json}
        response = self.client.get(self.api_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '[]')

    def test_handle_bad_json(self):
        response = self.client.get(self.api_url, {'query': 'bad'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(True, 'JSON' in response.content)

    def test_api_jsonp(self):
        # query string
        callback = 'jsonpCallback'
        response = self.client.get(self.api_url, {'callback': callback})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.startswith(callback + '('), True)
        self.assertEqual(response.content.endswith(')'), True)
        start = callback.__len__() + 1
        end = response.content.__len__() - 1
        content = response.content[start: end]
        d = dict_for_mongo_without_userform_id(self.xform.surveys.all()[0].parsed_instance)
        find_d = simplejson.loads(content)[0]
        self.assertEqual(sorted(find_d, key=find_d.get), sorted(d, key=d.get))

    def test_api_with_query_start_limit(self):
        # query string
        json = '{"transport/available_transportation_types_to_referral_facility":"none"}'
        data = {'query': json, 'start': 0, 'limit': 10}
        response = self.client.get(self.api_url, data)
        self.assertEqual(response.status_code, 200)
        d = dict_for_mongo_without_userform_id(self.xform.surveys.all()[0].parsed_instance)
        find_d = simplejson.loads(response.content)[0]
        self.assertEqual(sorted(find_d, key=find_d.get), sorted(d, key=d.get))

    def test_api_count(self):
        # query string
        json = '{"transport/available_transportation_types_to_referral_facility":"none"}'
        data = {'query': json, 'count': 1}
        response = self.client.get(self.api_url, data)
        self.assertEqual(response.status_code, 200)
        find_d = simplejson.loads(response.content)[0]
        self.assertTrue(find_d.has_key('count'))
        self.assertEqual(find_d.get('count'), 1)

    def test_api_column_select(self):
        # query string
        json = '{"transport/available_transportation_types_to_referral_facility":"none"}'
        columns = '["transport/available_transportation_types_to_referral_facility"]'
        data = {'query': json, 'fields': columns}
        response = self.client.get(self.api_url, data)
        self.assertEqual(response.status_code, 200)
        find_d = simplejson.loads(response.content)[0]
        self.assertTrue(find_d.has_key('transport/available_transportation_types_to_referral_facility'))
        self.assertFalse(find_d.has_key('_attachments'))