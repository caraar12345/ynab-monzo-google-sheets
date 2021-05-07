## Sync YNAB with Monzo Plus / Google Sheets

If you have a Monzo Plus/Premium account, your transactions will be automatically synchronised with Google Sheets.

This Python script will read from your Google Sheet and synchronise these further into You Need A Budget.

You'll need 3 files in the same folder as `main.py` - these are `options.json`, `ynab-auth.json` and `google-auth.json`.

`options.json` and `ynab-auth.json` both have `.sample` versions in this repo which you will need to rename then fill in.

`google-auth.json` is a Service Account authentication file from [Google Cloud](https://cloud.google.com/iam/docs/creating-managing-service-account-keys). You'll need to share your Monzo Transactions Google Sheet with the Service Account.

[**@juampynr/google-spreadsheet-reader**](https://github.com/juampynr/google-spreadsheet-reader) has a great guide as to how to set this up!
