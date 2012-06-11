import settings
from odk_viewer.models import ParsedInstance, DataDictionary
from pyxform.section import Section, RepeatingSection
from pyxform.survey import Survey
from pyxform.question import Question
from pandas import *
from utils.export_tools import question_types_to_exclude

xform_instances = settings.MONGO_DB.instances

def build_workbook_for(username, id_string):
    """
    Creates a workbook composed of multiple sheets
    """
    w = WorkBook()
    dd = DataDictionary.objects.get(user__username=username, id_string=id_string)




    query = {ParsedInstance.USERFORM_ID: u'%s_%s' % (username, id_string)}
    #TODO: how to query 50 thousands records
    cursor = xform_instances.find(query)
    instances = list(instance for instance in cursor)
    #TODO: if instances is empty the DataFrame constructor throws
    return DataFrame(instances)

class Sheet(object):
    """
    Represents a single row/column data structure essentially a single DataFrame object
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
        self.sheets = {}

        # dictionary of sheet names with a list of columns/xpaths
        self.survey_sections = self._generate_survey_sections()

        # for each survey section get mongo db data and create sheet
        for sheet_name, sheet_columns in self.survey_sections.iteritems():
            # get mongo data matching username/id_string but only select sheet_columns
            select_columns = dict([(c, 1) for c in sheet_columns])
            query = {ParsedInstance.USERFORM_ID: u'%s_%s' % (username, id_string)}
            cursor = xform_instances.find(query, select_columns)
            data = [r for r in cursor]

            # add a sheet
            sheet = Sheet(data, sheet_columns)
            self.add_sheet(sheet_name, sheet)

    def _generate_survey_sections(self):
        dd = DataDictionary.objects.get(user__username=self.username, id_string=self.id_string)

        # the survey element/main sheet
        default_sheet_name = None

        # dictionary of sheet names with a list of columns/xpaths
        survey_sections = {}

        # get form elements to split repeats into separate sheets and everything else in the main sheet
        for e in dd.get_survey_elements():
            # check for a Section or sub-classes of
            if isinstance(e, Section):
                sheet_name = e.name

                # if its a survey set the default sheet name
                if isinstance(e, Survey):
                    default_sheet_name = sheet_name
                    survey_sections[default_sheet_name] = []

                # if a repeat we use its name otherwise use default sheet name
                if isinstance(e, RepeatingSection):
                    sheet_name = e.name
                    survey_sections[sheet_name] = []
                else:
                    sheet_name = default_sheet_name

                # for each child add to sheet
                for c in e.children:
                    if isinstance(c, Question) and not question_types_to_exclude(c.type):
                        survey_sections[sheet_name].append(c.get_abbreviated_xpath())

        return survey_sections

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