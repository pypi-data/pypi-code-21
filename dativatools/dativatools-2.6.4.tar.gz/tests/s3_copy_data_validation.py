import sys
import unittest
from dativatools.s3_lib import S3Lib
from dativatools.log import Logger
from boto.s3.connection import S3Connection

class test_s3_validation(unittest.TestCase):
    section = ''
    '''
    Class to perform testing of files upload/download from s3 bucket.
    '''
    config_dict = {'credentials': {'aws_access_key_id_optional': '',
                                   'aws_secret_access_key_optional': '',
                                   'environment_variables' : 'no',
                                   'bucket_name': '',
                                   'log_file_path': 'log/',
                                   'log_file_name':'s3_copy_data_valadation.txt'},
                   'insight_reduced': {'database': 'insightsreduced',
                                       'host': '',
                                       'port': ,
                                       'user': '',
                                       'password': '',
                                       'client': ''},
                   's3bucketURL': '',
                   'backup_on_s3': 'back_up_csv_files/',
                   'suffix_schema':'etl',
                   'suffix_bkp':'_bkp',
                   'suffix_ren':'_ren',
                   'csv_path' :'/home/renuka/',
                   'scriptfile': '/home/renuka/database_scripts/',
                   'all_tables': 'channel_info,schedule_info,ad_schedule_info,application_info,asn_info,browser_info,cdn_info,consumption_method_info,demogrp                                 hic_info,device_info,device_connection_type_info,geography_info,isp_info,package_info,purchasable_info,purchase_info,save_lo                                 cal_content_info,sso_info,subscriber_info,vod_info,gdd_user,gdd_save_result,gdd_purchasable,gdd_channel_audio_language,gdd_p                                 rogramme,gdd_package,gdd_isp,gdd_geography,gdd_epg,gdd_device,gdd_device_connection_type,gdd_device_attributes,gdd_demograph                                 ic,gdd_consumption_method,gdd_commercial_break,gdd_channel,gdd_channel_package,gdd_channel_attributes,gdd_cdn,gdd_browser,gd                                 d_autonomous_system_number,gdd_application,gdd_ad_promo,gdd_ad_schedule,gdd_start_result,gdd_start_cause,gdd_end_cause,gdd_s                                 ubscriber,gdd_subscriber_package,gdd_subscriber_user,gdd_subscriber_device,gdd_subscriber_attributes,playback_channel_info,p                                 layback_program_info,playback_local_info,gd_ci_ad_promo,gd_ci_consumption,gd_ci_ppv,gd_events,gd_ci_saved_content',
                   'staging_tables': 'channel_info,schedule_info',
                   'dimension_tables': 'gdd_user,gdd_save_result,gdd_purchasable,gdd_channel_audio_language,gdd_programme,gdd_package,gdd_isp,gdd_geography,g                                        dd_epg,gdd_device,gdd_device_connection_type,gdd_device_attributes,gdd_demographic,gdd_consumption_method,gdd_commerc                                        ial_break,gdd_channel,gdd_channel_package,gdd_channel_attributes,gdd_cdn,gdd_browser,gdd_autonomous_system_number,gdd                                        _application,gdd_ad_schedule,gdd_ad_promo,gdd_start_result,gdd_start_cause,gdd_end_cause,gdd_subscriber,gdd_subscribe                                        r_package,gdd_subscriber_user,gdd_subscriber_device,gdd_subscriber_attributes',
                   'fact_tables': 'gd_ci_ad_promo,gd_ci_consumption,gd_ci_ppv,gd_events,gd_ci_saved_content',
                   'final_tables': {'channel_info': 'gdd_channel,gdd_channel_attributes,gdd_channel_audio_language_c_info',
                   'schedule_info': 'gdd_programme_s_info,gdd_epg',
                                'ad_schedule_info': 'gdd_ad_schedule,gdd_commercial_break,gdd_ad_promo',
                                'application_info': 'gdd_application_ap_info',
                                'asn_info': 'gdd_autonomous_system_number',
                                'browser_info': 'gdd_browser',
                                'cdn_info': 'gdd_cdn',
                                'consumption_method_info': 'gdd_consumption_method',
                                'demographic_info': 'device_info',
                                'device_connection_type_info': 'gdd_device_connection_type',
                                'geography_info': 'gdd_geography',
                                'isp_info': 'gdd_isp',
                                'package_info': 'gdd_package,gdd_channel_package',
                                'playback_channel_info': 'gdd_session_pc_info',
                                'playback_program_info': 'gdd_session_pp_info',
                                'playback_local_info': 'gdd_session_pl_info',
                                'save_local_content_info': 'gd_ci_saved_content,gdd_save_result',
                                'sso_info': 'gdd_user_ss_info,gdd_application_ss_info,gd_events',
                                'subscriber_info': 'gdd_subscriber,gdd_subscriber_attributes,gdd_subscriber_device,gdd_user_sub_info,gdd_subscriber_user,gdd_subscriber_package',
                                'vod_info': 'gdd_programme_v_info,gdd_channel_audio_language_v_info'},
                 'email_config': {'send_from': 'renuka.lodaya@ardentisys.com',
                                 'send_to': 'renuka.lodaya@ardentisys.com',
                                 'cc': '',
                                 'subject': 'GD Reduce Job Failure',
                                 'smtplogin': 'genius.report@ardentisys.com',
                                 'smtppassword': 'Gen!us$R3port%13#',
                                 'smtpserver': 'mail.ardentisys.com:25'}}

    logger = Logger()
    logger_obj = logger.__get_logger__(config_dict['credentials']['log_file_path'], config_dict['credentials']['log_file_name'])
    # -------------------------------------------------------------------------
    #    Name: test_copy_data()
    #    Returns: True if test passses
    #    Raises: Exception if test fails
    #    Desc: This function is test that dat is copied from s3 to database
    # -------------------------------------------------------------------------
    def test_copy_data(self):
        tableList = self.config_dict['staging_tables'].split(",")
        for tablename in tableList:
            obj,con = self.get_s3_val_obj()
            result = obj.copy_data(tablename)
            self.assertTrue(result[0], True)        

    # -------------------------------------------------------------------------
    #    Name: get_s3_val_obj()
    #    Returns: Settings
    #    Raises: None
    #    Desc: This function is used to pass the config details.
    # -------------------------------------------------------------------------
    def get_s3_val_obj(self):
        obj = S3Lib(self.config_dict, logger_obj=self.logger_obj )
        con = obj.get_connection(self.config_dict)[2] 
        return obj, con


'''
This function is used to initialize the test run
'''


if __name__ == '__main__':
    unittest.main()
