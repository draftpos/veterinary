import frappe

def get_data():
	return {
		"fieldname": "quotation",
		"transactions": [
			{
				"label": "Medical Records",
				"items": ["Pet Order", "Admissions", "Procedure", "Pet History"]
			}
		]
	}
