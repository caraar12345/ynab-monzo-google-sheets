import os
import json
from typing import Literal
from apiclient import discovery
from google.oauth2 import service_account
import ynab_api
from ynab_api.rest import ApiException
from pprint import pprint
import ast
import datetime

ENVIRONMENT = "production"  # "production" or "staging"
DRYRUN = False

SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/spreadsheets"]
SECRET_FILE = os.path.join(os.getcwd(), 'google-auth.json')
OPTIONS_FILE = os.path.join(os.getcwd(), 'options.json')

with open(OPTIONS_FILE) as f:
    options = json.load(f)
    SPREADSHEET_ID = options["SPREADSHEET_ID"]
    RANGE_NAME = options["RANGE_NAME"]

    if ENVIRONMENT == "staging":
        YNAB_BUDGET_ID = options["STAGING_YNAB_BUDGET_ID"]
        YNAB_MONZO_ID = options["STAGING_YNAB_MONZO_ID"]

    elif ENVIRONMENT == "production":
        YNAB_BUDGET_ID = options["PROD_YNAB_BUDGET_ID"]
        YNAB_MONZO_ID = options["PROD_YNAB_MONZO_ID"]

    else:
        print("Invalid environment. Set an environment - staging or production.")
        quit()

YNAB_AUTH_FILE = os.path.join(os.getcwd(), 'ynab-auth.json')

with open(YNAB_AUTH_FILE) as f:
    ynab_auth_token = json.load(f)["access_token"]

configuration = ynab_api.Configuration()
configuration.api_key_prefix['Authorization'] = 'Bearer'
configuration.api_key['Authorization'] = ynab_auth_token
with ynab_api.ApiClient(configuration) as api_client:
    accounts_api_instance = ynab_api.AccountsApi(api_client)
with ynab_api.ApiClient(configuration) as api_client:
    txn_api_instance = ynab_api.TransactionsApi(api_client)


CREDENTIALS = service_account.Credentials.from_service_account_file(
    SECRET_FILE, scopes=SCOPES)
service = discovery.build('sheets', 'v4', credentials=CREDENTIALS)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                            range=RANGE_NAME).execute()
values = result.get('values', [])

potBalances = {}


def getYNABAccountList(budgetID):
    try:
        api_response = accounts_api_instance.get_accounts(budgetID)
        return ast.literal_eval(str(api_response))['data']['accounts']
    except ApiException as e:
        print("Exception when calling AccountsApi->get_accounts: %s\n" % e)


def ynabPotAccount(potName, accountList):
    fullPotDetails = next(
        account for account in accountList if account["name"] == potName)
    return fullPotDetails


def monzoTxnToYNAB(transaction, accountList):
    accountID = YNAB_MONZO_ID
    if transaction[3] == "Pot transfer":
        #potOrNot = True
        potDetails = ynabPotAccount(transaction[4], accountList)
        payeeID = potDetails['transfer_payee_id']
    txnDate = datetime.datetime.strptime(
        transaction[1], "%d/%m/%Y").strftime("%Y-%m-%d")
    amount = int(float(transaction[7])*1000)
    payeeName = transaction[4]
    cleared = "cleared"
    approved = "true"
    importID = transaction[0]
    try:
        memo = transaction[11]
    except IndexError:
        memo = ""

    if "payeeID" not in locals():
        payeeID = None

    txnJSON = json.dumps(
        {
            "transaction": {
                "account_id": accountID,
                "date": txnDate,
                "amount": amount,
                "payee_id": payeeID,
                "payee_name": payeeName,
                "memo": memo,
                "cleared": cleared,
                "approved": approved,
                "import_id": importID
            }
        }
    )

    finalTxn = ynab_api.SaveTransaction(
        account_id=accountID,
        date=txnDate,
        amount=amount,
        payee_id=payeeID,
        payee_name=payeeName,
        memo=memo,
        cleared='cleared',
        approved=True,
        import_id=importID
    )

    if DRYRUN:
        print(txnJSON)
    else:
        return finalTxn


if __name__ == "__main__":
    accountList = getYNABAccountList(YNAB_BUDGET_ID)
    if DRYRUN == True:
        for x in values:
            if x[0] != "Transaction ID":
                print(monzoTxnToYNAB(x, accountList))
    else:
        txnList = []
        for x in values:
            if x[0] != "Transaction ID":
                txnList.append(monzoTxnToYNAB(x, accountList))

        try:
            toPostToYNAB = ynab_api.SaveTransactionsWrapper(
                transactions=txnList)
            api_response = txn_api_instance.create_transaction(
                YNAB_BUDGET_ID, toPostToYNAB)
            pprint(api_response)
        except ApiException as e:
            print(
                "Exception when calling TransactionsApi->create_transaction: %s\n" % e)
            pprint(api_response)
