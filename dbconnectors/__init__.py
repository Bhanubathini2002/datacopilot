from .core import DBConnector
from .BQConnector import BQConnector,bq_specific_data_types
from .FirestoreConnector import FirestoreConnector
from utilities import (PROJECT_ID,BQ_REGION,BQ_OPENDATAQNA_DATASET_NAME,BQ_LOG_TABLE_NAME)

bqconnector = BQConnector(PROJECT_ID,BQ_REGION,BQ_OPENDATAQNA_DATASET_NAME,BQ_LOG_TABLE_NAME)
firestoreconnector = FirestoreConnector(PROJECT_ID,"opendataqna-session-logs")

__all__ = ["firestoreconnector","bqconnector"]
