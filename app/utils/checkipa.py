#coding=utf-8

from pprint import pprint
import sys
import os
import datetime
import tempfile
import shutil
import re
import zipfile
import plistlib
import optparse

DEFAULT_ENCODING = 'utf-8'
VERSION_NUMBER = '1.5'

#---------------------------------------------------------------------
# IntegrityCheck Class
#---------------------------------------------------------------------
class IntegrityCheck(object):
    '''TODO完善'''
    """This class reports and examines specific details and
    relationships between values in Info.plist and
    embedded.mobileprovision files"""

    def __init__(self, params):
        self.data = params['info']
        self.profile = params['mobileprovision']
        # self.verbose = params['verbose']
        self.ipa_filename = params['ipa_filename']

        self.warnings = {}
        self.errors = {}
        self.ipa_info = {}

        self._initialize_results_data()

        # run the checks
        self.process_checks()
        # self.output_report()

    def detect_errors(self):
        results = []

        if self.errors['ipa_failure']:
            results.append({'label': 'IPA File',
                            'description': 'Info.plist file is not accessable'})

        if self.errors['mobileprovision']:
            results.append({'label': 'Provision Profile',
                            'description': 'not located or accessable'})

        if self.errors['mobileprovision']:
            results.append({'label': 'Provision Profile',
                            'description': 'not located or accessable'})

        if self.errors['bundleid']:
            results.append({'label': 'BundleID',
                            'description': 'does not exist'})

        if self.errors['bundleseed']:
            results.append({'label': 'Bundleseed',
                            'description': 'does not exist'})

        if self.errors['version']:
            results.append({'label': 'Version',
                            'description': 'app version is not exist'})

        if self.errors['appid']:
            results.append({'label': 'AppID',
                            'description': 'does not exist or has a problem'})

        if self.errors['appid_malformed']:
            results.append({'label': 'AppID',
                            'description': 'formatted incorrectly'})

        if self.errors['appid_bundleseed_mismatch']:
            appid_parts = self.profile['Entitlements']['application-identifier'].split('.', 1)
            appid_suffix = appid_parts[1]
            bundleid_val = self.data['CFBundleIdentifier']
            desc = 'BundleID "%s" does not match AppID "%s"' % (bundleid_val, appid_suffix)
            results.append({'label': 'ID Mismatch', 'description': desc})

        if self.errors['appid_bundleid_mismatch']:
            results.append({'label': 'AppID',
                            'description': 'does not match the BundleID and is not wildcard'})

        if self.errors['distmethod']:
            results.append({'label': 'Distribution',
                            'description': 'not Enterprise and no provisioned devices'})

        if self.errors['dist_dev']:
            results.append({'label': 'Distribution',
                            'description': 'development profile not found'})

        if self.errors['dist_missing']:
            results.append({'label': 'Distribution',
                            'description': 'no distribution profile found'})

        if self.errors['expire_date_past']:
            exp_desc = '%s is in the past' % (self.profile['ExpirationDate'])
            results.append({'label': 'Expiration Date', 'description': exp_desc})

        return results
    # end detect_errors()

    def detect_warnings(self):
        results = []

        if self.warnings['push']:
            results.append({'label': 'Push Notification',
                            'description': 'not enabled'})

        if self.warnings['push_apsenv']:
            results.append({'label': 'Push Notification',
                            'description': 'aps-environment key is not set'})

        if self.warnings['dist_dev']:
            dist_warn_desc = "code signing Entitlements 'get-task-allow' value is set to YES; should be NO"
            results.append({'label': 'Distribution',
                            'description': dist_warn_desc})

        if self.warnings['expire_date_coming']:
            exp_desc = '%s is rapidly approaching' % (self.profile['ExpirationDate'])
            results.append({'label': 'Expiration Date', 'description': exp_desc})

        if self.warnings['interface_orientations']:
            exp_desc = 'UISupportedInterfaceOrientations and UISupportedInterfaceOrientations~ipad should contains `UIInterfaceOrientationPortrait` and `UIInterfaceOrientationPortraitUpsideDown` at least'
            results.append({'label': 'UISupportedInterfaceOrientations', 'description': exp_desc})

        return results
    # end detect_warnings()
    

    def output_report(self):
        report_warnings = self.detect_warnings()
        report_errors = self.detect_errors()

        vertical_spacer = ''

        # Heading
        main_heading = 'IPA File Integrity: "%s"' % (os.path.basename(self.ipa_filename))

        txt = []
        txt.append(vertical_spacer)
        txt.append(main_heading)
        txt.append('=' * len(main_heading))
        txt.append(vertical_spacer)

        # Info
        provisioned_devices = self.get_provisioned_devices()
        txt.append('Info')
        txt.append('-' * len('Info'))

        if 'CFBundleName' in self.data:
            txt.append('  Name: %s' % (self.data['CFBundleName']))

        if 'CFBundleVersion' in self.data:
            txt.append('  Version: %s' % (self.data['CFBundleVersion']))

        if ('ExpirationDate' in self.profile):
            txt.append('  Expiration Date: %s' % (self.profile['ExpirationDate']))

        if self.ipa_info['adhoc'] and not self.ipa_info['enterprise']:
            ipa_type = 'Ad Hoc/Developer'
        elif self.ipa_info['enterprise'] and not self.ipa_info['adhoc']:
            ipa_type = 'Enterprise'
        else:
            ipa_type = 'unknown'
            report_errors.append({'label': 'Distribution', 'description': 'unknown distribution type'})
        txt.append('  Distribution Profile Type: %s' % (ipa_type))

        if len(provisioned_devices) > 0:
            txt.append('  Provisioned Devices (%d): ' % (len(provisioned_devices)))
            for udid in provisioned_devices:
                txt.append('  %s' % (udid))
        else:
            txt.append('  Provisioned Devices (0):')

        txt.append(vertical_spacer)

        # Warnings
        txt.append('Warnings')
        txt.append('-' * len('Warnings'))
        if len(report_warnings) == 0:
            txt.append('  none')
        else:
            for war in report_warnings:
                txt.append('  %s: %s' % (war['label'], war['description']))

        txt.append(vertical_spacer)

        # Errors
        txt.append('Errors')
        txt.append('-' * len('Errors'))
        if len(report_errors) == 0:
            txt.append('  none')
        else:
            for err in report_errors:
                txt.append('  %s: %s' % (err['label'], err['description']))

        txt.append(vertical_spacer)

        for line in txt:
            print('    %s' % (line))

    # end output_report

    def get_provisioned_devices(self):
        if 'ProvisionedDevices' in self.profile:
            return self.profile['ProvisionedDevices']
        else:
            return []

    def process_checks(self):
        self.check_bundle_id()
        self.check_bundle_seed()
        self.check_version()
        self.check_appid()
        self.check_push()
        self.check_dist_method()
        self.check_dist_profile()
        self.check_expiration_date()
        self.check_interface_orientations()

    #add by hzwangzhiwei
    def check_interface_orientations(self):
        if 'UISupportedInterfaceOrientations' in self.data and 'UISupportedInterfaceOrientations~ipad' in self.data:
            should_be = set(['UIInterfaceOrientationPortrait', 'UIInterfaceOrientationPortraitUpsideDown'])
            if set(self.data['UISupportedInterfaceOrientations']) >= should_be and \
                set(self.data['UISupportedInterfaceOrientations~ipad']) >= should_be:
                return

        self.warnings['interface_orientations'] = True


    def check_expiration_date(self):
        if ('ExpirationDate' in self.profile):
            warning_period_in_days = 14
            expire_date = self.profile['ExpirationDate']
            difference_date = expire_date - datetime.datetime.today()
            days_until_expire = difference_date.days + 1
            if (days_until_expire > 0) and (days_until_expire <= warning_period_in_days):
                self.warnings['expire_date_coming'] = True
            elif days_until_expire <= 0:
                self.errors['expire_date_past'] = True

    # Checks whether a distribution certificate or a developer
    # certificate is present in mobileprovision
    #
    # Development signed apps typically set the 'get-task-allow' to True
    #
    # FIXME: 'dist_dev' should be conditionally set to errors or
    #         warnings, depending if we're in an Enterprise context
    #         or not. For now, we're choosing warnings as if we're
    #         in a developer context.
    def check_dist_profile(self):
        if 'get-task-allow' in self.profile['Entitlements']:
            if self.profile['Entitlements']['get-task-allow']:  # boolean, should be False
                self.warnings['dist_dev'] = True
        else:
            self.errors['dist_missing'] = True
    # end check_dist_profile

    def check_push(self):
        appid = None

        if 'Entitlements' in self.profile:
            if 'application-identifier' in self.profile['Entitlements']:
                appid = self.profile['Entitlements']['application-identifier']
            else:
                self.warnings['push'] = True
        else:
            self.warnings['push'] = True

        if 'Entitlements' in self.profile:
            if 'aps-environment' not in self.profile['Entitlements']:
                self.warnings['push'] = True
                self.warnings['push_apsenv'] = True

        if appid is not None:
            # split on only 1 (the first) period, thus returning 2
            # elements, if valid appid format
            appid_vals = appid.split('.', 1)

            # wildcard appid, not allowed for push
            if len(appid_vals) != 2:
                self.warnings['push'] = True
            elif appid_vals[1] == '*':
                self.ipa_info['wildcard'] = True
                self.warnings['push'] = True
    # end check_push()

    def check_appid(self):
        bundleseed = None
        bundleid = None
        appid = None

        if 'ApplicationIdentifierPrefix' in self.profile:
            if len(self.profile['ApplicationIdentifierPrefix']) > 0:
                bundleseed = self.profile['ApplicationIdentifierPrefix'][0]
        else:
            self.errors['appid'] = True

        if 'CFBundleIdentifier' in self.data:
            bundleid = self.data['CFBundleIdentifier']

        if 'Entitlements' in self.profile:
            if 'application-identifier' in self.profile['Entitlements']:
                appid = self.profile['Entitlements']['application-identifier']
            else:
                self.errors['appid'] = True
        else:
            self.errors['appid'] = True

        if appid is not None:
            # split on only 1 (the first) period, thus returning 2
            # elements, if valid appid format
            appid_vals = appid.split('.', 1)

            # wildcard appid, not allowed for push
            if len(appid_vals) != 2:
                # malformed appid: must have value.value
                self.errors['appid'] = True
                self.errors['appid_malformed'] = True
            elif appid_vals[1] == '*':
                self.ipa_info['wildcard'] = True

            # mismatch in mobileprovision profile
            if (bundleseed is not None) and (len(appid_vals) > 0):
                if bundleseed != appid_vals[0]:
                    self.errors['appid_bundleseed_mismatch'] = True

            # mismatch between info.plist and mobileprovision
            if (bundleid is not None) and (len(appid_vals) > 1) and not (self.ipa_info['wildcard']):
                appid_suffix = appid_vals[1]  # appid, excluding bundle seed id
                if not self.is_bundleid_match_against_appid(bundleid, appid_suffix):
                    self.errors['appid_bundleseed_mismatch'] = True
    # end check_appid

    # Apple's specified Entitlement app id is a string
    # _pattern_ against which the bundle id must match; the
    # two values do not have to be exactly the same. Example:
    #
    #     app id (excluding bundle seed id): com.apperian.*
    #                             bundle id: com.apperian.AppCatalog
    #
    # In this example there is no mismatch because the app
    # id's '*' wildcard allows any string to be used at that
    # part of the reverse domain string pattern.
    #
    # return boolean
    def is_bundleid_match_against_appid(self, bundleid, appid):
        if re.compile(r'\*').search(appid):

            wildcard_match = re.compile(r'[^*]+').search(appid)

            if wildcard_match is not None:
                appid_parts = appid.split('*', 1)
                bundleid_match = re.compile(r'^%s' % (appid_parts[0])).search(bundleid)
                return bundleid_match is not None

            # appid is only '*'; bundle id will always match
            else:
                return True

        # no wildcard; must be exact match
        else:
            return appid == bundleid
    # end is_bundleid_match_against_appid

    # if 'CFBundleIdentifier' key exists and is blank string: error
    # if 'CFBundleIdentifier' key not exists: error
    def check_bundle_id(self):
        if 'CFBundleIdentifier' in self.data:
            if self.data['CFBundleIdentifier'].strip() == "":
                self.errors['bundleid'] = True
        else:  # key missing
            self.errors['bundleid'] = True

    def check_version(self):
        if 'CFBundleVersion' in self.data:
            if self.data['CFBundleVersion'].strip() == "":
                self.errors['version'] = True
        else:
            self.errors['version'] = True



    def check_bundle_seed(self):
        if 'ApplicationIdentifierPrefix' in self.profile:
            app_id_prefix = self.profile['ApplicationIdentifierPrefix']
            if len(app_id_prefix) >= 1:
                if app_id_prefix[0].strip() == "":
                    self.errors['bundleseed'] = True
            else:
                self.errors['bundleseed'] = True
        else:
            self.errors['bundleseed'] = True

    def check_dist_method(self):
        if 'ProvisionsAllDevices' in self.profile:
            self.ipa_info['enterprise'] = True
        elif 'ProvisionedDevices' in self.profile:
            self.ipa_info['adhoc'] = True
        else:
            self.errors['distmethod'] = True

    def _initialize_results_data(self):
        # All errors and warnings are to be declared here and set to
        # false.  As new rules are discovered, they can be added here,
        # and then they can be handled by the caller.
        #
        # ipa_failure => The IPA file was not able to extract correctly, or
        #                did not conatin an info.plist
        #
        # mobileprovision => The embedded.mobileprovision file was not found
        #                   and thus the IPA does not have a provisioning profile
        #
        # bundleid => Bundleid key in info.plist either doesn't exist or is
        #             and empty string
        #
        # bundleseed => The bundleseed in mobileprovision either doesn't exist
        #               or is an empty string
        #
        # appid => The appid in mobileprovision has an error that makes it
        #          unacceptable, explained in further errors
        #
        # appid_malformed => The appid is not in the form of String.String
        #
        # appid_bundleseed_mismatch => The appid is not match the bundleseed
        #                              in the first value
        #
        # appid_bundleid_mismatch => The appid is not a wildcard and doesn't
        #                            match the bundleid in the second value
        #
        # distmethod => The app does not have a ProvisionedDevices (ad hoc) or
        #               ProvisionsAllDevices key
        #
        # dist_dev => This app has a development distribution profile and cannot be
        #             distributed
        #
        # dist_missing => This app is missing a distribution profile
        #
        # expire_date_past => Expiration date < tomorrow
        self.errors = {
            "ipa_failure": False,
            "mobileprovision": False,
            "bundleid": False,
            "version": False,
            "bundleseed": False,
            "appid": False,
            "appid_malformed": False,
            "appid_bundleseed_mismatch": False,
            "appid_bundleid_mismatch": False,
            "distmethod": False,
            "dist_dev": False,
            "dist_missing": False,
            "expire_date_past": False
        }

        # push => Push is disabled for this app
        #
        # push_apsenv => The aps-environment key is not set and thus
        # push disabled
        #
        # expire_date_coming => The expire date is within 14 days of
        # current date
        #
        #interface_orientations => the orientations of app, need to ['UIInterfaceOrientationPortrait', 'UIInterfaceOrientationPortraitUpsideDown']
        #UISupportedInterfaceOrientations and UISupportedInterfaceOrientations~ipad
        self.warnings = {
            "push": False,
            "push_apsenv": False,
            "dist_dev": False,
            "expire_date_coming": False,
            "interface_orientations": False
        }

        # IPA info contains information about the IPA that is
        # unrelated to errors or warnings, such as if it's an App
        # Catalog or is a wildcard application (meaning push is
        # disabled)
        #
        # app_catalog => This application is an App Catalog
        #
        # wildcard => This application has a wildcard provisioning profile
        #            meaning push is disabled
        #
        #
        # enterprise => This app has an Enterprise distribution
        # profile
        #
        # adhoc => This app has an Ad hoc distribution profile
        self.ipa_info = {
            "app_catalog": False,
            "wildcard": False,
            "enterprise": False,
            "adhoc": False}
    # end initializeResultsData

    def verbose_output(self):
        print('')
        print('INFO:')
        pprint(self.ipa_info)
        print('')

        print('WARNINGS:')
        pprint(self.warnings)
        print('')

        print('ERRORS:')
        pprint(self.errors)
        print('')

        print('checks completed: items marked True are problematic.')

    def to_result(self):
        result = {}
        result['warning'] = self.detect_warnings()
        result['error'] = self.detect_errors()

        return result
# end IntegrityCheck class


#---------------------------------------------------------------------
# ParseIPA class
#---------------------------------------------------------------------
class ParseIPA(object):
    plist_file_rx = re.compile(r'Payload/.+?\.app/Info.plist$')
    plist_misnamed_payload_file_rx = re.compile(r'payload/.+?\.app/Info.plist$')
    provision_file_rx = re.compile(r'\bembedded.mobileprovision$')
    xml_rx = re.compile(r'<\??xml')
    provision_xml_rx = re.compile(r'<\?xml.+</plist>', re.DOTALL)

    def __init__(self, ipa_filename):
        self.info_plist_data = {}
        self.provision_data = {}
        self.errors = []
        self.ipa_filename = ipa_filename
        self.full_path_plist_filename = ''
        self.temp_directory = ''
        self.extract_provision_data()
        self.extract_info_plist_data()
        self.rm_temp()

    def get_filename_from_ipa(self, filetype):
        zip_obj = zipfile.ZipFile(self.ipa_filename, 'r')

        if filetype == 'Info':
            regx = ParseIPA.plist_file_rx
        elif filetype == 'Misnamed_Payload_Check':
            regx = ParseIPA.plist_misnamed_payload_file_rx
        else:
            regx = ParseIPA.provision_file_rx

        filenames = zip_obj.namelist()
        filename = ''
        for fname in filenames:
            if regx.search(fname):
                filename = fname
                break
        return {'filename': filename, 'zip_obj': zip_obj}
    # end get_filename_from_ipa()

    def extract_provision_data(self):
        extract_info = self.get_filename_from_ipa('Provision')
        zip_obj = extract_info['zip_obj']
        provision_filename = extract_info['filename']

        data = {}
        if provision_filename == '':
            self.errors.append('embedded.mobileprovision file not found in IPA')
        else:
            content = zip_obj.read(provision_filename)
            match = ParseIPA.provision_xml_rx.search(content)
            if (match is not None):
                provision_xml_content = match.group()
                data = plistlib.readPlistFromString(provision_xml_content)
            else:
                self.errors.append('unable to parse embedded.mobileprovision file')

        self.provision_data = data
    # end extract_provision_data

    def extract_info_plist_data(self):
        extract_info = self.get_filename_from_ipa('Info')
        zip_obj = extract_info['zip_obj']
        plist_filename = extract_info['filename']

        data = {}
        if plist_filename == '':
            if self.get_filename_from_ipa('Misnamed_Payload_Check')['filename'] != '':
                self.errors.append("Payload folder is misnamed 'payload' (lower-case p). Rename to 'Payload'")
            else:
                self.errors.append('Info.plist file not found in IPA')
        else:
            content = zip_obj.read(plist_filename)
            if (ParseIPA.xml_rx.match(content)):
                data = plistlib.readPlistFromString(content)
            else:
                self.temp_directory = tempfile.mkdtemp()

                zip_obj.extract(plist_filename, self.temp_directory)
                fullpath_plist = '%s/%s' % (self.temp_directory, plist_filename)

                os_info = os.uname()
                if os_info[0] == 'Linux':
                    cmd = 'plutil -i "%s" -o "%s"' % (fullpath_plist, fullpath_plist)
                else:
                    cmd = 'plutil -convert xml1 "%s"' % (fullpath_plist)
                # pprint(cmd)

                os.system(cmd)
                data = plistlib.readPlist(fullpath_plist)
        # end if plist == ''

        self.info_plist_data = data
    # end extractPlist()

    def is_valid_zip_archive(self):
        return zipfile.is_zipfile(self.ipa_filename)

    def rm_temp(self):
        # clean up tmp directory tree
        try:
            if self.temp_directory != '':
                shutil.rmtree(self.temp_directory)
        except IOError, ex:
            print(str(ex))

    def app_name(self):
        if 'CFBundleDisplayName' in self.info_plist_data:
            return self.info_plist_data['CFBundleDisplayName']
        elif 'CFBundleName' in self.info_plist_data:
            return self.info_plist_data['CFBundleName']
        return ''
    
    def bundle_identifier(self):
        if 'CFBundleIdentifier' in self.info_plist_data:
            return self.info_plist_data['CFBundleIdentifier']
        return ''
    
    def target_os_version(self):
        if 'DTPlatformVersion' in self.info_plist_data:
            return re.findall('[\d\.]*', self.info_plist_data['DTPlatformVersion'])[0]
        return ''
    
    def minimum_os_version(self):
        if 'MinimumOSVersion' in self.info_plist_data:
            return re.findall('[\d\.]*', self.info_plist_data['MinimumOSVersion'])[0]
        return ''
        
    def version(self):
        if 'CFBundleVersion' in self.info_plist_data:
            return self.info_plist_data['CFBundleVersion']
        return ''
    
    def icon_file_name(self):
        if 'CFBundleIcons' in self.info_plist_data and \
            'CFBundlePrimaryIcon' in self.info_plist_data["CFBundleIcons"] and \
            'CFBundleIconFiles' in self.info_plist_data["CFBundleIcons"]["CFBundlePrimaryIcon"]:
            icons = self.info_plist_data["CFBundleIcons"]["CFBundlePrimaryIcon"]['CFBundleIconFiles']
            if icons != None and len(icons) > 0:
                return icons[len(icons) - 1]
        elif 'CFBundleIcons~ipad' in self.info_plist_data and \
            'CFBundlePrimaryIcon' in self.info_plist_data["CFBundleIcons~ipad"] and \
            'CFBundleIconFiles' in self.info_plist_data["CFBundleIcons~ipad"]["CFBundlePrimaryIcon"]:
            icons = self.info_plist_data["CFBundleIcons~ipad"]["CFBundlePrimaryIcon"]['CFBundleIconFiles']
            if icons != None and len(icons) > 0:
                return icons[len(icons) - 1]
        else:
            return False
    
    def icon_file_path(self):
        icon_file_name = self.icon_file_name()
        if icon_file_name:
            zfile = zipfile.ZipFile(self.ipa_filename)
            zip_name_list = zfile.namelist()
            for name in zip_name_list:
                tempkey = ".app/" + icon_file_name
                if tempkey in name:
                    zfile.close()
                    return name
            zfile.close()
            
            return False
    
    def mv_icon_to(self, file_name):
        icon_path = self.icon_file_path()
        if icon_path:
            zfile = zipfile.ZipFile(self.ipa_filename)
            
            icon_file =  open(file_name, "wb")
            icon_file.write(zfile.read(icon_path))
            icon_file.close()
            zfile.close()
            return True
    
        return False

    def get(self, key):
        if key in self.info_plist_data:
            return self.info_plist_data[key]
        elif key in self.provision_data:
            return self.provision_data[key]
        return '' 

    def distribution_profile_type(self):
        adhoc = False
        enterprise = False

        if 'ProvisionsAllDevices' in self.provision_data:
            enterprise = True
        elif 'ProvisionedDevices' in self.provision_data:
            adhoc = True
        else:
            pass

        if adhoc and not enterprise:
            ipa_type = 'Ad Hoc/Developer'
        elif enterprise and not adhoc:
            ipa_type = 'Enterprise'
        else:
            ipa_type = 'unknown'
        
        return ipa_type

    def expiration_date(self):
        if 'ExpirationDate' in self.provision_data:
            return self.provision_data['ExpirationDate']
        else:
            return ''

    def provisioned_devices(self):
        if 'ProvisionedDevices' in self.provision_data:
            return self.provision_data['ProvisionedDevices']
        else:
            return []

    def to_check_params(self):
        return {'info': self.info_plist_data, 'mobileprovision': self.provision_data, 'ipa_filename': self.ipa_filename}
# end ParseIPA class


#test usage function
def process_ipa(ipa_filename):
    check_result = {}

    parse = ParseIPA(ipa_filename)
    #infomation
    check_result['name'] = parse.app_name()
    check_result['version'] = parse.version()
    check_result['bundle_id'] = parse.bundle_identifier()
    check_result['tar_version'] = parse.target_os_version()
    check_result['min_version'] = parse.minimum_os_version()

    check_result['expiration'] = parse.expiration_date()
    check_result['profile_type'] = parse.distribution_profile_type()
    check_result['provisioned_devices'] = parse.provisioned_devices()

    #warning and error
    check_result['warning'] = []
    check_result['error'] = []

    if len(parse.errors) == 0:
        Integrity_check = IntegrityCheck(parse.to_check_params())
        # Integrity_check.output_report()
        result = Integrity_check.to_result()
        check_result['warning'] = result['warning']
        check_result['error'] = result['error']

    else:
        #parse error, need save to log, and to opt the code
        pprint(parse.errors)

    # print check_result
    return check_result
# end process_ipa


if __name__ == '__main__':
    print sys.argv[1]
    ipa_filename = sys.argv[1]
    process_ipa(ipa_filename)
    sys.exit(0)
