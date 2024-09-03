# Copyright (c) 2024, 1 and contributors
# For license information, please see license.txt

# import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": "haha",
			"fieldname": "cewqeqe1",
			"fieldtype": "Data",
		},
		{
			"label": "12321321",
			"fieldname": "3213213213",
			"fieldtype": "Int",
		},
	]


def get_data() -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	return [
		["123123", 1],
		["123213123", 2],
	]

def get_filters():
    return [
        {
            "fieldname": "from_date",
            "label": "从日期",
            "fieldtype": "Date",

        },
        {
            "fieldname": "to_date",
            "label": "到日期",
            "fieldtype": "Date",

        }
    ]
