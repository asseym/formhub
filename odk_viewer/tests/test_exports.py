from main.tests.test_base import MainTestCase
from django.core.urlresolvers import reverse
from odk_logger.views import download_xlsform
from odk_viewer.xls_writer import XlsWriter
from odk_viewer.pandas_mongo_bridge import get_index_and_key, get_groupname_from_xpath

class TestExports(MainTestCase):
    def test_unique_xls_sheet_name(self):
        xls_writer = XlsWriter()
        xls_writer.add_sheet('section9_pit_latrine_with_slab_group')
        xls_writer.add_sheet('section9_pit_latrine_without_slab_group')
        # create a set of sheet names keys
        sheet_names_set = set(xls_writer._sheets.keys())
        self.assertEqual(len(sheet_names_set), 2)

    def test_get_index_and_key_from_xpath_with_index(self):
        xpath = "my/test/path/with[2]/index"
        expected_index = 2
        expected_key = "my/test/path/with/index"
        index, key = get_index_and_key(xpath)
        self.assertEqual(expected_index, index)
        self.assertEqual(expected_key, key)

    def test_get_index_and_key_from_xpath_without_index(self):
        xpath = "my/test/path/without/index"
        expected_index = 1
        expected_key = "my/test/path/without/index"
        index, key = get_index_and_key(xpath)
        self.assertEqual(expected_index, index)
        self.assertEqual(expected_key, key)

    def test_groupname_from_xpath_with_index(self):
        xpath = "my/test/path/with[2]/index"
        expected_group_name = "my/test/path/with"
        group_name = get_groupname_from_xpath(xpath)
        self.assertEqual(expected_group_name, group_name)

    def test_groupname_from_xpath_without_index(self):
        xpath = "my/test/path/without/index"
        expected_group_name = "my/test/path/without"
        group_name = get_groupname_from_xpath(xpath)
        self.assertEqual(expected_group_name, group_name)

    def test_groupname_from_ungrouped_xpath(self):
        xpath = "xpath"
        group_name = get_groupname_from_xpath(xpath)
        self.assertEqual(None, group_name)

    def test_groupname_from_single_group_xpath(self):
        xpath = "my/xpath"
        expected_group_name = "my"
        group_name = get_groupname_from_xpath(xpath)
        self.assertEqual(expected_group_name, group_name)
