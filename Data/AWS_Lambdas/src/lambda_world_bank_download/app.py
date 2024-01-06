from WorldBankApiHandler import WorldBankApiHandler


def handler(event, context):
    api_handler = WorldBankApiHandler()
    api_handler.update_world_bank_indicators(2)
    print('Done')
