import unittest

import vat_moss_lite.errors
import vat_moss_lite.id

from .unittest_data import DataDecorator, data


@DataDecorator
class IdTests(unittest.TestCase):
    @staticmethod
    def valid_ids():
        # These are all read, valid VAT IDs that we test against
        # VIES and data.brreg.no
        return (
            ('at', 'ATU 38289400', 'ATU38289400', 'AT'),
            ('be', 'BE0844.044.609', 'BE0844044609', 'BE'),
            ('bg', 'BG160072254', 'BG160072254', 'BG'),
            ('cy', 'CY 10132211L', 'CY10132211L', 'CY'),
            ('cz', 'CZ15046575', 'CZ15046575', 'CZ'),
            ('de', 'DE 129273398', 'DE129273398', 'DE'),
            ('dk', 'DK 65 19 68 16', 'DK65196816', 'DK'),
            ('ee', 'EE 100 366 327', 'EE100366327', 'EE'),
            ('el', 'EL 094259216', 'EL094259216', 'GR'),
            ('gr', 'GR094259216', 'EL094259216', 'GR'),
            ('es', 'ES B58378431', 'ESB58378431', 'ES'),
            ('fi', 'FI- 2077474-0', 'FI20774740', 'FI'),
            ('fr', 'FR 35 552049447', 'FR35552049447', 'FR'),
            ('hr', 'HR76639357285', 'HR76639357285', 'HR'),
            ('hu', 'HU17780010', 'HU17780010', 'HU'),
            ('ie', 'IE6388047V', 'IE6388047V', 'IE'),
            ('it', 'IT05175700482', 'IT05175700482', 'IT'),
            ('lt', 'LT120212314', 'LT120212314', 'LT'),
            ('lu', 'LU26888617', 'LU26888617', 'LU'),
            ('lv', 'LV40003032949', 'LV40003032949', 'LV'),
            ('mt', 'MT20681625', 'MT20681625', 'MT'),
            ('nl', 'NL 004495445 B01', 'NL004495445B01', 'NL'),
            ('no', 'NO974760673MVA', 'NO974760673MVA', 'NO'),
            ('pl', 'PL 7740001454', 'PL7740001454', 'PL'),
            ('pt', 'pt 502332743', 'PT502332743', 'PT'),
            ('ro', 'RO 24063308', 'RO24063308', 'RO'),
            ('se', 'SE 556012579001', 'SE556012579001', 'SE'),
            ('si', 'si47992115', 'SI47992115', 'SI'),
            ('sk', 'sk2020270780', 'SK2020270780', 'SK'),
            ('al', 'AL J 61929021 E', None, None),
        )

    @staticmethod
    def invalid_ids():
        return (('GBGD000',), ('IE000000',), ('AT1',))

    @data('valid_ids', True)
    def normalize(self, vat_id, expected_normalized_vat_id, expected_country_code):
        result = vat_moss_lite.id.normalize(vat_id)
        self.assertEqual(expected_normalized_vat_id, result)

    @data('valid_ids', True)
    def validate_id(self, vat_id, expected_normalized_vat_id, expected_country_code):
        try:
            result = vat_moss_lite.id.validate(vat_id)
            if result:
                country_code, normalized_vat_id, name = result
                self.assertEqual(expected_country_code, country_code)
                self.assertEqual(expected_normalized_vat_id, normalized_vat_id)
            else:
                self.assertEqual(expected_normalized_vat_id, result)
        except vat_moss_lite.errors.WebServiceUnavailableError:
            return unittest.skip('VIES webservice unavailable')

    @data('invalid_ids')
    def validate_id_invalid(self, vat_id):
        self.assertRaises(vat_moss_lite.errors.InvalidError, vat_moss_lite.id.validate, vat_id)
