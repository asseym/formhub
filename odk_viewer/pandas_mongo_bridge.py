import settings
from odk_viewer.models import ParsedInstance, DataDictionary
from pyxform.section import Section, RepeatingSection
from pyxform.survey import Survey
from pyxform.question import Question
from pandas import *
from utils.export_tools import question_types_to_exclude
from odk_viewer.models.parsed_instance import flatten_mongo_cursor
import re

xform_instances = settings.MONGO_DB.instances

def xpath_to_dot_notation(xpath):
    # convert slashes to dots for mongo query
    return re.sub("/", ".", xpath[1:]) # slice remove initial slash i.e. /survey/question to survey/question

def get_index_and_key(key):
    """
    Get unique key and index embedded inside a repeat key that looks like "repeat[2]/item"
    """

    #the first item does not have a index, it is just "repeat/item" so set defaults to:
    index = 1
    new_key = key

    # strip out the index i.e. repeat[2]/item and use it as a key to other items in the same repeat
    match = re.match(r"(.+?)\[(\d+)\](.+)", key)
    # the first item does not have a index i.e its simply repeat/item
    if match:
        groups = match.groups()
        new_key = groups[0] + groups[2]
        index = int(groups[1])
    return index, new_key

def get_groupname_from_xpath(xpath):
    # check if xpath has an index
    match = re.match(r"(.+?)\[\d+\]/", xpath)
    if match:
        return match.groups()[0]
    else:
        #TODO: optimize re to capture entire group
        # need to strip out the question name and leave just the group name
        matches = re.findall(r"(.+?)/", xpath)
        if len(matches) > 0:
            return "/".join(matches)
        else:
            return None

class Sheet(object):
    """
    Represents a single row->column data structure essentially a single pandas DataFrame object
    """

    def __init__(self, data, columns):
        """
        Initialize

        data - a list of dictionary objects compatible with DataFrame constructor
        columns - a list of columns to use
        """
        self.columns = columns
        self.dataframe = DataFrame(data, columns=columns)

    def get_num_columns(self):
        return len(self.columns)

    def get_column_at(self, index):
        return self.columns[index]

    def get_num_rows(self):
        pass

    def get_row_at(self):
        pass

class WorkBook(object):
    """
    XLS Workbook-like structure with a number of sheets
    """
    def __init__(self, username, id_string):
        self.username = username
        self.id_string = id_string

    def _append_data_for_sheet_name(self, data, sheet_name):
        """
        Checks if data already has the key "sheet_name", creates if it doesnt and appends the record
        """
        if not data.has_key(sheet_name):
            data[sheet_name] = 0

    def _build_survey_sections(self):
        self.default_sheet_name = None
        dd = DataDictionary.objects.get(user__username=self.username, id_string=self.id_string)

        # the survey element/main sheet
        #TODO: find a way to set this here instead of waiting for it to be caught in the loop, bad things could happen
        default_sheet_name = None

        # dictionary of sheet names with a list of columns/xpaths
        self.survey_sections = {}

        # get form elements to split repeats into separate sheets and everything else in the main sheet
        for e in dd.get_survey_elements():
            # check for a Section or sub-classes of
            if isinstance(e, Section):
                sheet_name = e.get_abbreviated_xpath()

                # if its a survey set the default sheet name
                if isinstance(e, Survey):
                    self.survey_sections[sheet_name] = []
                    self.default_sheet_name = sheet_name

                # if a repeat we use its name
                if isinstance(e, RepeatingSection):
                    self.survey_sections[sheet_name] = []
                #otherwise use default sheet name
                else:
                    sheet_name = self.default_sheet_name

                assert(self.default_sheet_name)
                # for each child add to survey_sections
                for c in e.children:
                    if isinstance(c, Question) and not question_types_to_exclude(c.type):
                        self.survey_sections[sheet_name].append(c.get_abbreviated_xpath())

    def _build_sheets(self):
        self.sheets = {}

        # dictionary of sheet names with a list of columns/xpaths
        self._build_survey_sections()

        # get mongo data matching username/id_string
        query = {ParsedInstance.USERFORM_ID: u'%s_%s' % (self.username, self.id_string)}
        cursor = xform_instances.find(query)
        data = {}
        # split the records by sheet_name
        for record in cursor:
            new_sheet_name = self.default_sheet_name
            # a dict of the different records we will end up with, grouped by sheet name
            records = {}
            for key, val in record.iteritems():
                index = 1 # used to combine repeats that belong to the same index since they are treated
                # as separate records
                new_key = key
                for sheet_name in self.survey_sections:
                    # check if key matches any of our sheet names meaning its a repeat
                    group_name = get_groupname_from_xpath(key)
                    if group_name and group_name == sheet_name:
                        new_sheet_name = sheet_name
                        index, new_key = get_index_and_key(key)
                        break

                if not records.has_key(new_sheet_name):
                    records[new_sheet_name] = {}

                if not records[new_sheet_name].has_key(index):
                    records[new_sheet_name][index] = {}

                # index into the dict of records and append our data there
                records[new_sheet_name][index].update({new_key: val})

            # records now contains a sheet name as the key and number of dicts which we now need to convert to lists
            for sheet_name, records_dict in records.iteritems():
                if not data.has_key(sheet_name):
                    data[sheet_name] = []
                for record in records_dict.itervalues():
                    data[sheet_name].append(record)

        # for each survey section, create sheet
        for sheet_name, sheet_columns in self.survey_sections.iteritems():
            # add a sheet
            sheet = Sheet(data[sheet_name], sheet_columns)
            self.add_sheet(sheet_name, sheet)

    def add_sheet(self, name, sheet):
        self.sheets[name] = sheet

    def get_num_sheets(self):
        return len(self.sheets)

    def get_sheet(self, name):
        return self.sheets[name]


class WorkbookExporter(object):
    """
    Base class for data exporters
    """
    def __init(self):
        pass

class CSVWorkbookExporter(WorkbookExporter):
    """
    CSV file exporter
    """
    def __init__(self):
        pass