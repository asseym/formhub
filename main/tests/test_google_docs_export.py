from django.core.urlresolvers import reverse

from main.models import TokenStorageModel
from main.google_export import token, refresh_access_token
from odk_viewer.views import google_xls_export

from test_base import MainTestCase

class TestGoogleDocsExport(MainTestCase):

    def setUp(self):
        self.token = token
        self.refresh_token = '1/ISGBd-OBWr-RbXN2Fq879Xht1inmg_n4sJ_Wd4CoQNk'
        self.token.refresh_token = self.refresh_token
        self._create_user_and_login()

    def test_google_docs_export(self):
        self._publish_transportation_form()
        self._make_submissions()
        self._refresh_token()
        self.assertEqual(TokenStorageModel.objects.all().count(), 1)
        response = self.client.get(reverse(google_xls_export, kwargs={
            'username': self.user.username,
            'id_string': self.xform.id_string
        }))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://docs.google.com')
        # share the data, log out, and check the export
        self._share_form_data()
        self._logout()
        response = self.client.get(reverse(google_xls_export, kwargs={
            'username': self.user.username,
            'id_string': self.xform.id_string
        }))
        self.assertEqual(response.status_code, 302)

    def _refresh_token(self):
        self.assertEqual(TokenStorageModel.objects.all().count(), 0)
        self.assertIsNone(self.token.access_token)
        self.token = refresh_access_token(self.token, self.user)
        self.assertIsNotNone(self.token.access_token)
        self.assertEqual(TokenStorageModel.objects.all().count(), 1)
