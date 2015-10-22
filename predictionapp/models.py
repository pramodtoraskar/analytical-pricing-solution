# -*- coding: utf-8 -*-

import xlrd
import tables
import re
import datetime
from django.db import models
from django.conf import settings

# Create your models here.

OIL_TYPE_CONTENT_SHEET_START = 6
OIL_TYPE_CONTENT_SHEET_END = 13

class SeedData(models.Model):
    doc_file = models.FileField(upload_to='seed_data/%Y/%m/%d')


class OilType(models.Model):
    oil_type = models.CharField(max_length=100)
    of_series = models.IntegerField()
    sheet_name = models.CharField(max_length=100)


class SourceKey(models.Model):
    source_key = models.CharField(max_length=200)


class OilDescSourceKeyMapping(models.Model):
    oil_desc = models.ForeignKey(OilType)
    sheet_name = models.CharField(max_length=100)
    source_key = models.ForeignKey(SourceKey)
    column_number = models.IntegerField()


class OilProductionByMonthBySingleCol(tables.IsDescription):
    """Data model class for oil production by month"""

    date = tables.StringCol(16)
    barrel_price = tables.Float64Col()

class OilProductionByMonthByTwoCol(tables.IsDescription):
    """Data model class for oil production by month"""

    date = tables.StringCol(16)
    barrel_price_of_series1 = tables.Float64Col()
    barrel_price_of_series2 = tables.Float64Col()

class OilProductionByMonthByMulCol(tables.IsDescription):
    """Data model class for oil production by month"""

    date = tables.StringCol(16)
    barrel_price_of_series1 = tables.Float64Col()
    barrel_price_of_series2 = tables.Float64Col()
    barrel_price_of_series3 = tables.Float64Col()


class ExcelToHdf5(object):
    """Create hdf5 file from excel workbook"""

    def __init__(self, xls_filename, hdf5_filename, supported_sheets=None):
        """Convert given filename to hdf5"""

        self.xls_filename = xls_filename
        self.hdf5_filename = hdf5_filename

        self.workbook = None
        self.hdf5_file = None
        self.no_sheets = 0
        self.oil_type_list = []

        # Sheet indexes we support
        if supported_sheets is None:
            self.supported_sheets = [1, 2]
        else:
            self.supported_sheets = supported_sheets

        # Table for each sheet in xls file
        self.tables = []

    def load_xls_data(self):
        """Load data from given xls filename"""

        self.workbook = xlrd.open_workbook(filename=self.xls_filename)
        self.no_sheets = self.workbook.nsheets

        content_sheet = self.workbook.sheet_by_index(0)
        self.oil_type_list = [[content_sheet.row_slice(rowx=type_range,
                                                       start_colx=1,
                                                       end_colx=5)[0].value,
                               content_sheet.row_slice(rowx=type_range,
                                                       start_colx=1,
                                                       end_colx=5)[1].value,
                               content_sheet.row_slice(rowx=type_range,
                                                       start_colx=1,
                                                       end_colx=5)[2].value]
                         for type_range in range(OIL_TYPE_CONTENT_SHEET_START,
                                                 OIL_TYPE_CONTENT_SHEET_END)]
        self.supported_sheets = [supported_sheets_count
                                 for supported_sheets_count in
                                 range(1, len(self.oil_type_list)+1)]

    def create_hdf5_file(self):
        """Create hdf5 file with given filename, return file and table"""

        # Open a file in "w"rite mode
        self.hdf5_file = tables.openFile(self.hdf5_filename,
                                         mode="w",
                                         title="Oil Production by Month")

        # Create a new group under "/" (root)
        group_single = self.hdf5_file.createGroup('/',
                                                  'data_single_group',
                                                  'Production by Month '
                                                  'with Single Series')

        group_two = self.hdf5_file.createGroup('/',
                                               'data_two_group',
                                               'Production by two series with '
                                               'Mul')

        group_mul = self.hdf5_file.createGroup('/',
                                               'data_mul_group',
                                               'Production by Month with Mul')

        for sheet_idx in self.supported_sheets:

            table_name = re.sub('[^A-Za-z0-9]+', '',
                                self.oil_type_list[sheet_idx-1][1])

            if int(self.oil_type_list[sheet_idx-1][2]) == 1:

                table = self.hdf5_file.createTable(
                    group_single,
                    table_name.lower(),
                    OilProductionByMonthBySingleCol,
                    "Oil Production By Month with Single Series")
            elif int(self.oil_type_list[sheet_idx-1][2]) == 2:

                table = self.hdf5_file.createTable(
                    group_two,
                    table_name.lower(),
                    OilProductionByMonthByTwoCol,
                    "Oil Production By Month with Mul Series")
            else:
                table = self.hdf5_file.createTable(
                    group_mul,
                    table_name.lower(),
                    OilProductionByMonthByMulCol,
                    "Oil Production By Month with Mul Series")

            self.tables.append(table)

    def convert_xldate_to_timestamp(self, xldate, data_book):
        """Convert an xldate tuple (from xlrd.xldate_as_tuple) to timestamp"""

        xldate = xlrd.xldate_as_tuple(xldate, data_book.datemode)
        date = datetime.datetime(xldate[0], xldate[1], xldate[2])

        return str(date)

    def _convert_overall_two_sheet(self, data_sheet, hdf5_row):

        for row in range(3, data_sheet.nrows):
            values = data_sheet.row_values(row)[:3]
            if values[2]:
                hdf5_row['barrel_price_of_series1'] = values[2]
            else:
                hdf5_row['barrel_price_of_series1'] = None
            if values[1]:
                hdf5_row['barrel_price_of_series2'] = values[1]
            else:
                hdf5_row['barrel_price_of_series2'] = None

            hdf5_row['date'] = self.convert_xldate_to_timestamp(values[0],
                                                                self.workbook)
            hdf5_row.append()

    def _convert_overall_mul_sheet(self, data_sheet, hdf5_row):

        for row in range(3, data_sheet.nrows):
            values = data_sheet.row_values(row)[:4]
            if values[3]:
                hdf5_row['barrel_price_of_series3'] = values[3]
            else:
                hdf5_row['barrel_price_of_series3'] = None
            if values[2]:
                hdf5_row['barrel_price_of_series2'] = values[2]
            else:
                hdf5_row['barrel_price_of_series2'] = None
            if values[1]:
                hdf5_row['barrel_price_of_series1'] = values[1]
            else:
                hdf5_row['barrel_price_of_series1'] = None

            hdf5_row['date'] = self.convert_xldate_to_timestamp(values[0],
                                                                self.workbook)
            hdf5_row.append()

    def _convert_overall_single_sheet(self, data_sheet, hdf5_row):

        for row in range(3, data_sheet.nrows):
            values = data_sheet.row_values(row)[:2]
            if values[1]:
                hdf5_row['barrel_price'] = values[1]
            else:
                hdf5_row['barrel_price'] = None

            hdf5_row['date'] = self.convert_xldate_to_timestamp(values[0],
                                                                self.workbook)
            hdf5_row.append()

    def populate_hdf5(self, sheet_idx, hdf5_table):
        """Populate given hdf5 table with given data"""

        data_sheet = self.workbook.sheet_by_index(sheet_idx)

        if int(self.oil_type_list[sheet_idx-1][2]) == 1:
            self._convert_overall_single_sheet(data_sheet, hdf5_table.row)
        elif int(self.oil_type_list[sheet_idx-1][2]) == 2:
            self._convert_overall_two_sheet(data_sheet, hdf5_table.row)
        else:
            self._convert_overall_mul_sheet(data_sheet, hdf5_table.row)

    def populate_oildesc_sourcekey_mapping(self):
        for sheet_idx in self.supported_sheets:
            data_sheet = self.workbook.sheet_by_index(sheet_idx)
            sourcekey_values_list = data_sheet.row_values(1)[1:]
            data_sheet_name = str(data_sheet.name)
            for idx, sourcekey_name in enumerate(sourcekey_values_list):
                source_key_obj, created = SourceKey.objects.get_or_create(
                    source_key=str(sourcekey_name))
                oil_type_obj = OilType.objects.get(sheet_name =
                                                   data_sheet_name)
                column_num = idx+1
                oil_desc_source_key_mapping_obj, created = \
                OilDescSourceKeyMapping.objects.get_or_create(
                    oil_desc = oil_type_obj,
                    sheet_name = data_sheet_name,
                    source_key = source_key_obj,
                    column_number = column_num)


    def convert(self):
        """Convert excel sheet to hdf5 file"""

        self.load_xls_data()

        for oil_type in self.oil_type_list:
            oil_type_obj, created = OilType.objects.get_or_create(
                oil_type = str(oil_type[1]),
                of_series = int(oil_type[2]),
                sheet_name=  str(oil_type[0]))

        self.populate_oildesc_sourcekey_mapping()

        self.create_hdf5_file()

        for sheet_idx, table in zip(self.supported_sheets, self.tables):
            self.populate_hdf5(sheet_idx, table)

        self.hdf5_file.close()

def convert_xls_to_hdf5(xls_filename, hdf5_filename):
    """ Convert xls to hdf5 database """

    if not xls_filename:
        raise 'Need seed data file!'

    converter = ExcelToHdf5(xls_filename, hdf5_filename)
    converter.convert()
