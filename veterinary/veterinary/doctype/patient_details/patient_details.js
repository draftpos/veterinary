// Copyright (c) 2026, Veterinary Contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient Details', {
	onload(frm) {
		frm.disable_save();
		_fix_patient_name_visibility(frm);
		_load_histories(frm);
	},

	refresh(frm) {
		frm.disable_save();
		_fix_patient_name_visibility(frm);
		_load_histories(frm);
	}
});

function _fix_patient_name_visibility(frm) {
	// Frappe hides the autoname field by default — force it visible
	frm.set_df_property('patient_name', 'hidden', 0);
	frm.set_df_property('patient_name', 'read_only', 1);
	frm.refresh_field('patient_name');
}

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

			// ── Vaccinations ──────────────────────────────────────────
			_render_table('vaccinations-table', d.vaccinations_history, [
				{ key: 'vaccination_id', label: 'Record ID', is_link: true, doctype: 'Vaccinations' },
				{ key: 'vaccine',              label: 'Vaccine' },
				{ key: 'batch',               label: 'Batch' },
				{ key: 'date',                label: 'Date' },
				{ key: 'user',                label: 'Administered By' },
				{ key: 'status',              label: 'Status' },
				{ key: 'next_follow_up_date', label: 'Next Follow Up' }
			]);

			// ── Procedures ────────────────────────────────────────────
			_render_table('procedures-table', d.procedures_history, [
				{ key: 'name',          label: 'Record ID', is_link: true, doctype: 'Procedure' },
				{ key: 'doctor_name',   label: 'Doctor' },
				{ key: 'patient_owner', label: 'Patient Owner' },
				{ key: 'start_time',    label: 'Start Time' },
				{ key: 'end_time',      label: 'End Time' }
			]);

			// ── Prescriptions ─────────────────────────────────────────
			_render_table('prescriptions-table', d.prescriptions_history, [
				{ key: 'order_id', label: 'Order ID', is_link: true, doctype: 'Pet Order' },
				{ key: 'item_name', label: 'Medication' },
				{ key: 'quantity', label: 'Qty' },
				{ key: 'dosage',   label: 'Dosage' },
				{ key: 'date',     label: 'Date' }
			]);

			// ── Medical Examination ───────────────────────────────────
			_render_table('medical-exam-table', d.medical_exam_history, [
				{ key: 'name',      label: 'Record ID', is_link: true, doctype: 'Pet Order' },
				{ key: 'complaint', label: 'Complaint' },
				{ key: 'diagnosis', label: 'Diagnosis' },
				{ key: 'advices',   label: 'Advices' },
				{ key: 'hyd',       label: 'HYD' },
				{ key: 'crt',       label: 'CRT' },
				{ key: 'weight',    label: 'Weight (kg)' },
				{ key: 'rr',        label: 'RR' },
				{ key: 'hr',        label: 'HR' },
				{ key: 'modified',  label: 'Date' }
			]);

			// ── Admissions ────────────────────────────────────────────
			_render_table('admissions-table', d.admissions_history, [
				{ key: 'name',          label: 'Record ID', is_link: true, doctype: 'Admissions' },
				{ key: 'quotation',     label: 'Quotation', is_link: true, doctype: 'Quotation' },
				{ key: 'bed_no',        label: 'Bed No' },
				{ key: 'doctorname',    label: 'Doctor' },
				{ key: 'checkin_time',  label: 'Check In' },
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

	const headers = columns.map(c => `<th style="white-space:nowrap;">${c.label}</th>`).join('');
	const body = rows.map(row => {
		const cells = columns.map(c => {
			const val = row[c.key] != null ? row[c.key] : '';
			if (c.is_link && val) {
				return `<td><a href="#" onclick="frappe.set_route('Form','${c.doctype}','${val}');return false;">${val}</a></td>`;
			}
			return `<td>${val}</td>`;
		}).join('');
		return `<tr>${cells}</tr>`;
	}).join('');

	container.innerHTML = `
		<div style="overflow-x:auto;">
			<table class="table table-bordered table-hover table-sm" style="margin:0;min-width:100%;">
				<thead style="background:var(--gray-100);position:sticky;top:0;">
					<tr>${headers}</tr>
				</thead>
				<tbody>${body}</tbody>
			</table>
		</div>`;
}