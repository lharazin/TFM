from oecd_indicators import download_all_oecd_indicators


def handler(event, context):
    """ OECD Lambda – reads all indicators from official API and
    saves values to the database if any new records are available """

    download_all_oecd_indicators()
    print('Done')
