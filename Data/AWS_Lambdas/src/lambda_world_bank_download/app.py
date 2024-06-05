from WorldBankApiHandler import WorldBankApiHandler


def handler(event, context):
    """ World Bank Lambda – reads worlds bank yearly indicators
    from API using third-party wbgapi library. """

    api_handler = WorldBankApiHandler()
    api_handler.update_world_bank_indicators(2)
    print('Done')
