import settings
from odk_viewer.models import ParsedInstance, DataDictionary
from pandas import *

xform_instances = settings.MONGO_DB.instances

def build_workbook_for(username, id_string):
    """
    Creates a workbook composed of multiple sheets
    """


    # get form elements to split repeats into separate sheets


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

    def get_name(self):
        return self.name

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
    def __init__(self):
       pass

    def add_sheet(self, sheet):
        self.sheets.append(sheet)

    def get_num_sheets(self):
        return len(self.sheets)

    def get_sheet_at(self, index):
        return self.sheets[index]


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