from oecd_indicators import download_all_oecd_indicators


def handler(event, context):
    download_all_oecd_indicators()
    print('Done')
