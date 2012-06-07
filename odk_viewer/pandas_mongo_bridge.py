import settings
from odk_viewer.models import ParsedInstance
from pandas import *

xform_instances = settings.MONGO_DB.instances

def build_dataframe_for(username, id_string):
    """
    Converts mongo db data objects into pandas DataFrames
    """
    query = {ParsedInstance.USERFORM_ID: u'%s_%s' % (username, id_string)}
    #TODO: how to query 50 thousands records
    cursor = xform_instances.find(query)
    instances = list(instance for instance in cursor)
    #TODO: if instances is empty the DataFrame constructor throws
    return DataFrame(instances)

