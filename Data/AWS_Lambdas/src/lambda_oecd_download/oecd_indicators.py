from oecd_api import get_oecd_data


def download_all_oecd_indicators():
    """ Helper methods to read all OECD indicators in one funtion. """

    # 2. GDP
    get_oecd_data(indicator='QNA', subject='B1_GE', measure='GYSA', freq='Q',
                  countries_before_subject=True,
                  file_name='GDP Annual Growth Rate',
                  only_save_to_database=True)

    get_oecd_data(indicator='QNA', subject='B1_GE', measure='GPSA', freq='Q',
                  countries_before_subject=True,
                  file_name='GDP Growth Rate',
                  only_save_to_database=True)

    get_oecd_data(indicator='QNA', subject='B1_GE', measure='HVPVOBARSA',
                  freq='Q', countries_before_subject=True,
                  file_name='GDP Per Capita',
                  only_save_to_database=True)

    get_oecd_data(indicator='SNA_TABLE1', subject='B1_GE', measure='VXCOB',
                  freq='', countries_before_subject=True,
                  file_name='GDP Current Prices US Dollars',
                  with_measure=False, filter_measure_on_df=True,
                  only_save_to_database=True)

    get_oecd_data(indicator='SNA_TABLE1', subject='B1_GE', measure='VPCOB',
                  freq='', countries_before_subject=True,
                  file_name='GDP Current Prices PPP',
                  with_measure=False, filter_measure_on_df=True,
                  only_save_to_database=True)

    # 3. Labour
    get_oecd_data(indicator='KEI', subject='LRHUTTTT', measure='ST', freq='M',
                  file_name='Unemployment Rate', only_save_to_database=True)

    get_oecd_data(indicator='KEI', subject='LRHUTTTT', measure='ST', freq='Q',
                  file_name='Unemployment Rate Quarterly',
                  only_save_to_database=True)

    # 4. Prices
    get_oecd_data(indicator='KEI', subject='CPALTT01', measure='GY', freq='M',
                  file_name='Inflation Rate', only_save_to_database=True)

    get_oecd_data(indicator='KEI', subject='CPALTT01', measure='GY', freq='Q',
                  file_name='Inflation Rate Quarterly',
                  only_save_to_database=True)

    get_oecd_data(indicator='KEI', subject='CPALTT01', measure='GP', freq='M',
                  file_name='Inflation Rate MoM', only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='CPALTT01', measure='IXOB',
                  freq='M', countries_before_subject=True,
                  file_name='CPI', only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='PIEAFD01', measure='IXOB',
                  freq='M', countries_before_subject=True,
                  file_name='PPI Manufacture of food products',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='PIEAMP01', measure='IXOB',
                  freq='M', countries_before_subject=True,
                  file_name='PPI Manufacturing', only_save_to_database=True)

    # 5. Money
    get_oecd_data(indicator='KEI', subject='IRSTCI01', measure='ST', freq='M',
                  file_name='Overnight Interbank Rate',
                  only_save_to_database=True)

    get_oecd_data(indicator='KEI', subject='IR3TIB01', measure='ST', freq='M',
                  file_name='Short Term Interest Rate',
                  only_save_to_database=True)

    get_oecd_data(indicator='KEI', subject='IRLTLT01', measure='ST', freq='M',
                  file_name='Long Term Interest Rate',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='MANMM101', measure='ST', freq='M',
                  countries_before_subject=True,
                  file_name='Narrow Money M1', only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='MABMM301', measure='ST', freq='M',
                  countries_before_subject=True,
                  file_name='Broad Money M3', only_save_to_database=True)

    # 6. Trade
    get_oecd_data(indicator='KEI', subject='B6BLTT02', measure='ST', freq='Q',
                  file_name='Current Account to GDP',
                  only_save_to_database=True)

    get_oecd_data(indicator='QNA', subject='P6', measure='GYSA', freq='Q',
                  countries_before_subject=True,
                  file_name='Export of goods and services',
                  only_save_to_database=True)

    get_oecd_data(indicator='QNA', subject='P7', measure='GYSA', freq='Q',
                  countries_before_subject=True,
                  file_name='Import of goods and services',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='XTEXVA01', measure='CXML',
                  freq='M', countries_before_subject=True,
                  file_name='Export - Value (goods)',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='XTIMVA01', measure='CXML',
                  freq='M', countries_before_subject=True,
                  file_name='Import - Value (goods)',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='XTNTVA01', measure='CXML',
                  freq='M', countries_before_subject=True,
                  file_name='Net Trade - Value (goods)',
                  only_save_to_database=True)

    # 7. Government
    get_oecd_data(indicator='FIN_IND_FBS', subject='DBTADJS13GDP',
                  measure='', freq='', with_freq=False,
                  countries_before_subject=True,
                  file_name='Government Debt to GDP',
                  with_measure=False,
                  only_save_to_database=True)

    get_oecd_data(indicator='SNA_TABLE12', subject='GTE.GS13',
                  measure='', freq='',
                  countries_before_subject=True,
                  file_name='Total Government Expenditure',
                  with_measure=False,
                  only_save_to_database=True)

    get_oecd_data(indicator='SNA_TABLE12', subject='GTR.GS13',
                  measure='', freq='',
                  countries_before_subject=True,
                  file_name='Total Government Revenue',
                  with_measure=False,
                  only_save_to_database=True)

    # 8. Bussiness
    get_oecd_data(indicator='MEI_CLI', subject='BSCICP03', measure='',
                  freq='M', with_measure=False,
                  file_name='OECD Bussiness Confidence Indicator',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI_CLI', subject='LOLITOAA', measure='',
                  freq='M', with_measure=False,
                  file_name='OECD Composite Leading Indicator',
                  only_save_to_database=True)

    get_oecd_data(indicator='KEI', subject='PRINTO01', measure='GY', freq='M',
                  file_name='Industrial Production',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='PRMNTO01', measure='IXOBSA',
                  freq='M', countries_before_subject=True,
                  file_name='Total Manufacturing',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='PRINTO01', measure='IXOBSA',
                  freq='M', countries_before_subject=True,
                  file_name='Total Industry ex Construction',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='PRCNTO01', measure='IXOBSA',
                  freq='M', countries_before_subject=True,
                  file_name='Total Construction',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='NAEXCP05', measure='STSA',
                  freq='Q', countries_before_subject=True,
                  file_name='Changes in Inventories',
                  only_save_to_database=True)

    # 9. Customers
    get_oecd_data(indicator='MEI_CLI', subject='CSCICP03', measure='',
                  freq='M', with_measure=False,
                  file_name='OECD Consumer Confidence Indicator',
                  only_save_to_database=True)

    get_oecd_data(indicator='KEI', subject='NAEXKP02', measure='GY', freq='Q',
                  file_name='Private Consumption',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='SLRTTO02', measure='IXOBSA',
                  freq='M', countries_before_subject=True,
                  file_name='Total Retail Sales Value',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='SLRTCR03', measure='IXOBSA',
                  freq='M', countries_before_subject=True,
                  file_name='Passenger Car Registration',
                  only_save_to_database=True)

    get_oecd_data(indicator='MEI', subject='ODCNPI03', measure='IXOBSA',
                  freq='M', countries_before_subject=True,
                  file_name='Permits Issued (Residential Buildings)',
                  only_save_to_database=True)
