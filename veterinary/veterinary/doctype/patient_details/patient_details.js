// Copyright (c) 2026, Veterinary Contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient Details', {
	onload(frm) {
		frm.disable_save();
		_load_histories(frm);
	},

	refresh(frm) {
		frm.disable_save();
	}
});

function _load_histories(frm) {
	if (!frm.doc.patient_name) return;

	frappe.call({
		method: 'veterinary.veterinary.doctype.patient_details.patient_details.get_patient_history',
		args: { patient_name: frm.doc.patient_name },
		freeze: true,
		freeze_message: __('Loading patient history...'),
		callback(r) {
			if (!r.message) return;
			const d = r.message;
			_render_table('vaccinations-table', d.vaccinations_history, [
				{ key: 'name', label: 'ID' },
				{ key: 'modified', label: 'Last Modified' }
			]);
			_render_table('procedures-table', d.procedures_history, [
				{ key: 'name', label: 'ID' },
				{ key: 'doctor_name', label: 'Doctor' },
				{ key: 'start_time', label: 'Start Time' },
				{ key: 'end_time', label: 'End Time' }
			]);
			_render_table('prescriptions-table', d.prescriptions_history, [
				{ key: 'name', label: 'ID' },
				{ key: 'complaint', label: 'Complaint' },
				{ key: 'diagnosis', label: 'Diagnosis' },
				{ key: 'modified', label: 'Date' }
			]);
			_render_table('medical-exam-table', d.medical_exam_history, [
				{ key: 'name', label: 'ID' },
				{ key: 'complaint', label: 'Complaint' },
				{ key: 'diagnosis', label: 'Diagnosis' },
				{ key: 'modified', label: 'Date' }
			]);
			_render_table('admissions-table', d.admissions_history, [
				{ key: 'name', label: 'ID' },
				{ key: 'checkin_time', label: 'Check In' },
				{ key: 'checkout_time', label: 'Check Out' }
			]);
		}
	});
}

function _render_table(container_id, rows, columns) {
	// HTML fields render in a wrapper — find by id inside the form wrapper
	const container = document.getElementById(container_id);
	if (!container) return;

	if (!rows || rows.length === 0) {
		container.innerHTML = `<p class="text-muted" style="padding:12px;">No records found.</p>`;
		return;
	}

	const headers = columns.map(c => `<th>${c.label}</th>`).join('');
	const body = rows.map(row => {
		const cells = columns.map(c => {
			const val = row[c.key] || '';
			// Make the ID column a clickable link
			if (c.key === 'name') {
				return `<td><a href="#" onclick="frappe.set_route('Form', '${_doctype_for(container_id)}', '${val}'); return false;">${val}</a></td>`;
			}
			return `<td>${val}</td>`;
		}).join('');
		return `<tr>${cells}</tr>`;
	}).join('');

	container.innerHTML = `
		<table class="table table-bordered table-hover" style="margin:0;">
			<thead style="background:var(--gray-50);">
				<tr>${headers}</tr>
			</thead>
			<tbody>${body}</tbody>
		</table>`;
}

function _doctype_for(container_id) {
	const map = {
		'vaccinations-table':  'Vaccinations',
		'procedures-table':    'Procedure',
		'prescriptions-table': 'Pet Order',
		'medical-exam-table':  'Pet Order',
		'admissions-table':    'Admissions'
	};
	return map[container_id] || '';
}