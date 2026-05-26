// Copyright (c) 2026, Veterinary Contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient Details', {
	onload(frm) {
		if (frm.is_new() && frm.doc.patient_name === 'Bruno') {
			frm.set_value('patient_name', '');
		}
		frm.disable_save();
		_fix_patient_name_visibility(frm);
		_load_histories(frm);
	},

	refresh(frm) {
		// Silently trigger URL migration back to plain ID in background if any are still formatted
		if (!frm.is_new() && frm.doc.name !== frm.doc.patient_name) {
			frappe.call({
				method: 'veterinary.veterinary.doctype.patient_details.patient_details.migrate_patient_details_urls',
				callback: function(r) {
					if(r.message) {
						frappe.msgprint("Migration restored " + r.message + " Patient Details records back to plain integer IDs. Please refresh the page!");
					}
				}
			});
		}

		if (frm.is_new() && frm.doc.patient_name === 'Bruno') {

			frm.set_value('patient_name', '');
		}
		frm.disable_save();
		_fix_patient_name_visibility(frm);
		_load_histories(frm);
	}
});

function _fix_patient_name_visibility(frm) {
	// Frappe hides the autoname field by default — force it visible
	frm.set_df_property('patient_name', 'hidden', 0);
	frm.set_df_property('patient_name', 'read_only', frm.is_new() ? 0 : 1);

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

			// ── General Information Button ────────────────────────────
			try {
				const general_info = $(frm.fields_dict['general_info_html'].wrapper);
				if (general_info.length && !general_info.find('.btn-group-general').length) {
					const btn_group = $('<div class="btn-group-general" style="margin-bottom:15px; display:flex; flex-wrap:wrap; gap:10px; padding:10px; border:1px solid var(--border-color); background:var(--gray-50); border-radius:4px;">')
						.prependTo(general_info);

					$('<button class="btn btn-xs btn-info btn-goto-history">')
						.html('<i class="fa fa-list"></i> ' + __('Pet History List'))
						.on('click', () => {
							frappe.set_route('List', 'Pet History', {
								patient_name: frm.doc.patient_name
							});
						})
						.appendTo(btn_group);
				}
			} catch (e) { console.error("Error adding history button", e); }

			// ── Vaccinations Button ───────────────────────────────────
			try {
				const vaccinations_section = $(frm.fields_dict['vaccinations_html'].wrapper);
				if (vaccinations_section.length && !vaccinations_section.find('.btn-add-vaccination').length) {
					$('<button class="btn btn-xs btn-primary btn-add-vaccination" style="margin-top:10px; margin-bottom:10px;">')
						.html('<i class="fa fa-plus"></i> ' + __('Add New Vaccination'))
						.on('click', () => {
							frappe.new_doc('Vaccinations', {
								patient_name: frm.doc.patient_name
							});
						})
						.prependTo(vaccinations_section);
				}
			} catch (e) { console.error("Error adding vaccination button", e); }

			// ── Procedures Buttons ────────────────────────────────────
			try {
				const procedures_section = $(frm.fields_dict['procedures_html'].wrapper);
				if (procedures_section.length && !procedures_section.find('.btn-add-procedure').length) {
					const btn_group = $('<div class="btn-group-procedures" style="margin-top:10px; margin-bottom:10px; display:flex; gap:10px;">')
						.prependTo(procedures_section);

					$('<button class="btn btn-xs btn-primary btn-add-procedure">')
						.html('<i class="fa fa-plus"></i> ' + __('Add New Procedure'))
						.on('click', () => {
							frappe.new_doc('Procedure', {
								patient_name: frm.doc.patient_name,
								patient_owner: frm.doc.patient_owner
							});
						})
						.appendTo(btn_group);

					$('<button class="btn btn-xs btn-default btn-create-invoice">')
						.html('<i class="fa fa-file-text-o"></i> ' + __('Create Invoice'))
						.on('click', () => {
							frappe.call({
								method: 'veterinary.veterinary.doctype.patient_details.patient_details.get_procedure_invoice_data',
								args: { patient_name: frm.doc.patient_name },
								freeze: true,
								freeze_message: __('Preparing invoice...'),
								callback(r) {
									if (!r.message) return;
									const data = r.message;

									if (!data.items || data.items.length === 0) {
										frappe.msgprint({
											title: __('No Procedure Items'),
											message: __('No drug/item records were found in the procedures for this patient. Please add items to the Procedure record first.'),
											indicator: 'orange'
										});
										return;
									}

									// Build the invoice document
									const invoice = {
										customer: data.customer,
										remarks: `Veterinary invoice for patient: ${data.pet_name}`,
										items: data.items.map(i => ({
											item_code: i.item_code,
											item_name: i.item_name,
											qty: i.qty,
											rate: i.rate,
											description: i.description
										}))
									};

									frappe.new_doc('Sales Invoice', invoice);
								}
							});
						})
						.appendTo(btn_group);
						
					// Add a placeholder for Billable Procedures
					$('<div id="billable-procedures-list" style="margin-top:20px; border-top:1px solid var(--border-color); padding-top:10px;">')
						.appendTo(procedures_section);
				}
				
				_load_billable_procedures(frm);
				_load_reminder_settings(frm);
				_load_inventory(frm);
			} catch (e) { console.error("Error adding procedure buttons", e); }

			// ── Prescriptions Button ──────────────────────────────────
			try {
				const prescriptions_section = $(frm.fields_dict['prescriptions_html'].wrapper);
				if (prescriptions_section.length && !prescriptions_section.find('.btn-add-prescription').length) {
					$('<button class="btn btn-xs btn-primary btn-add-prescription" style="margin-top:10px; margin-bottom:10px;">')
						.html('<i class="fa fa-plus"></i> ' + __('Add New Prescription'))
						.on('click', () => {
							frappe.new_doc('Pet Order', {
								patient_name: frm.doc.patient_name,
								patient_owner: frm.doc.patient_owner
							});
						})
						.prependTo(prescriptions_section);
				}
			} catch (e) { console.error("Error adding prescription button", e); }

			// ── Admissions Button ─────────────────────────────────────
			try {
				const admissions_section = $(frm.fields_dict['admissions_html'].wrapper);
				if (admissions_section.length && !admissions_section.find('.btn-add-admission').length) {
					$('<button class="btn btn-xs btn-primary btn-add-admission" style="margin-top:10px; margin-bottom:10px;">')
						.html('<i class="fa fa-plus"></i> ' + __('Add New Admission'))
						.on('click', () => {
							frappe.new_doc('Admissions', {
								patient_name: frm.doc.patient_name,
								patient_owner: frm.doc.patient_owner
							});
						})
						.prependTo(admissions_section);
				}
			} catch (e) { console.error("Error adding admission button", e); }

			// ── Medical Examination Button ────────────────────────────
			try {
				const medical_exam_section = $(frm.fields_dict['medical_exam_html'].wrapper);
				if (medical_exam_section.length && !medical_exam_section.find('.btn-add-medical-exam').length) {
					$('<button class="btn btn-xs btn-primary btn-add-medical-exam" style="margin-top:10px; margin-bottom:10px;">')
						.html('<i class="fa fa-plus"></i> ' + __('New Medical Exam'))
						.on('click', () => {
							frappe.new_doc('Pet Order', {
								patient_name: frm.doc.patient_name,
								patient_owner: frm.doc.patient_owner
							});
						})
						.prependTo(medical_exam_section);
				}
			} catch (e) { console.error("Error adding medical exam button", e); }

			// ── Vaccinations ──────────────────────────────────────────
			_render_table('vaccinations-table', d.vaccinations_history, [
				{ key: 'vaccination_id', label: 'Traceability No', is_link: true, doctype: 'Vaccinations' },
				{ key: 'vaccine',              label: 'Vaccine' },
				{ key: 'batch',               label: 'Batch' },
				{ key: 'date',                label: 'Date' },
				{ key: 'user',                label: 'Administered By' },
				{ key: 'status',              label: 'Status' },
				{ key: 'next_follow_up_date', label: 'Next Follow Up' }
			]);

			// ── Procedures ────────────────────────────────────────────
			_render_table('procedures-table', d.procedures_history, [
				{ key: 'name',          label: 'Procedure No', is_link: true, doctype: 'Procedure' },
				{ key: 'quotation',     label: 'Quotation/Ref', is_link: true, doctype: 'Quotation' },
				{ key: 'doctor_name',   label: 'Doctor' },
				{ key: 'drug_item',     label: 'Drug' },
				{ key: 'quantity',      label: 'Qty' },
				{ key: 'dosage',        label: 'Dosage' },
				{ key: 'instructions',  label: 'Instructions' },
				{ key: 'start_time',    label: 'Start Time' }
			]);

			// ── Prescriptions ─────────────────────────────────────────
			_render_table('prescriptions-table', d.prescriptions_history, [
				{ key: 'order_id', label: 'Order No', is_link: true, doctype: 'Pet Order' },
				{ key: 'quotation', label: 'Quotation/Ref', is_link: true, doctype: 'Quotation' },
				{ key: 'item_name', label: 'Medication' },
				{ key: 'quantity', label: 'Qty' },
				{ key: 'dosage',   label: 'Dosage' },
				{ key: 'date',     label: 'Date' }
			]);

			// ── Medical Examination ───────────────────────────────────
			_render_table('medical-exam-table', d.medical_exam_history, [
				{ key: 'name',      label: 'Exam No', is_link: true, doctype: 'Pet Order' },
				{ key: 'quotation', label: 'Quotation/Ref', is_link: true, doctype: 'Quotation' },
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
				{ key: 'name',          label: 'Admission No', is_link: true, doctype: 'Admissions' },
				{ key: 'quotation',     label: 'Quotation/Ref', is_link: true, doctype: 'Quotation' },
				{ key: 'bed_no',        label: 'Bed No' },
				{ key: 'doctorname',    label: 'Doctor' },
				{ key: 'checkin_time',  label: 'Check In' },
				{ key: 'checkout_time', label: 'Check Out' }
			]);
		}
	});
}

function _load_billable_procedures(frm) {
	const container = $('#billable-procedures-list');
	if (!container.length) return;

	frappe.call({
		method: 'veterinary.veterinary.doctype.patient_details.patient_details.get_billable_procedures',
		callback(r) {
			if (r.message && r.message.length > 0) {
				let html = `
					<h6 style="margin-bottom:10px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">
						<i class="fa fa-info-circle"></i> ${__('Available Billable Procedures')}
					</h6>
					<div style="max-height:300px; overflow-y:auto; border:1px solid var(--border-color); border-radius:4px;">
						<table class="table table-sm table-hover" style="margin:0; font-size:12px;">
							<thead>
								<tr style="background:var(--gray-50);">
									<th>${__('Procedure Name')}</th>
									<th>${__('Item Code')}</th>
									<th class="text-right">${__('Standard Rate')}</th>
								</tr>
							</thead>
							<tbody>
				`;
				
				r.message.forEach(item => {
					html += `
						<tr>
							<td><strong>${item.item_name}</strong></td>
							<td><code>${item.item_code}</code></td>
							<td class="text-right">${frappe.format(item.standard_rate, { fieldtype: 'Currency' })}</td>
						</tr>
					`;
				});
				
				html += `
							</tbody>
						</table>
					</div>
					<p class="text-muted" style="font-size:11px; margin-top:5px;">
						${__('Note: These items are managed in the Item list under the "Procedures" group.')}
					</p>
				`;
				container.html(html);
			} else {
				container.html(`<p class="text-muted" style="font-size:12px;">${__('No billable procedures found in the "Procedures" item group.')}</p>`);
			}
		}
	});
}

function _load_reminder_settings(frm) {
	const container = $('#reminder-settings-dashboard');
	if (!container.length) return;

	frappe.db.get_value('Patient Name', frm.doc.patient_name, 'stop_vaccination_reminders', (r) => {
		const stop = r.stop_vaccination_reminders || 0;
		_render_reminder_settings(frm, stop);
	});
}

function _render_reminder_settings(frm, stop) {
	const container = $('#reminder-settings-dashboard');
	const status_text = stop ? 
		'<span class="label label-danger">Reminders Paused</span>' : 
		'<span class="label label-success">Reminders Active</span>';
	
	const btn_class = stop ? 'btn-success' : 'btn-danger';
	const btn_text = stop ? 'Resume Reminders' : 'Stop Reminders';
	const btn_icon = stop ? 'fa-play' : 'fa-stop';

	container.html(`
		<div style="padding:20px; border:1px solid var(--border-color); border-radius:8px; background:var(--gray-50); max-width:600px;">
			<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
				<h5 style="margin:0;">Vaccination Follow-up Reminders</h5>
				${status_text}
			</div>
			
			<p class="text-muted" style="font-size:13px; margin-bottom:20px;">
				Automated Email, SMS, and WhatsApp reminders are sent to the patient owner 3 days and 1 day before the next vaccination date.
			</p>
			
			<div style="display:flex; gap:10px;">
				<button class="btn btn-sm ${btn_class} btn-toggle-reminders">
					<i class="fa ${btn_icon}"></i> ${btn_text}
				</button>
				<button class="btn btn-sm btn-default btn-test-reminder">
					<i class="fa fa-paper-plane"></i> Send Test Reminder
				</button>
			</div>
			
			<div id="reminder-log" style="margin-top:20px; font-size:11px; color:var(--text-muted);">
				<i class="fa fa-clock-o"></i> Reminders are sent daily via system scheduler.
			</div>
		</div>
	`);

	container.find('.btn-toggle-reminders').on('click', () => {
		frappe.call({
			method: 'veterinary.veterinary.doctype.patient_details.patient_details.toggle_reminders',
			args: { patient_name: frm.doc.patient_name, stop: stop ? 0 : 1 },
			callback: (r) => {
				if (r.message && r.message.status === 'success') {
					frappe.show_alert({
						message: stop ? __('Reminders resumed') : __('Reminders stopped'),
						indicator: stop ? 'green' : 'red'
					});
					_load_reminder_settings(frm);
				}
			}
		});
	});

	container.find('.btn-test-reminder').on('click', () => {
		frappe.confirm(__('Send a test reminder to the patient owner?'), () => {
			frappe.call({
				method: 'veterinary.veterinary.doctype.patient_details.patient_details.send_vaccination_reminders',
				callback: (r) => {
					frappe.msgprint(__('Test reminder process triggered. Check Communication log for results.'));
				}
			});
		});
	});
}

function _load_inventory(frm) {
	const container = $('#veterinary-stock-table');
	if (!container.length) return;

	frappe.call({
		method: 'veterinary.veterinary.doctype.patient_details.patient_details.get_warehouse_stock',
		callback(r) {
			if (r.message && r.message.length > 0) {
				let html = `
					<h6 style="margin-bottom:15px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">
						<i class="fa fa-cubes"></i> ${__('Current Veterinary Inventory')}
					</h6>
					<div style="overflow-x:auto;">
						<table class="table table-sm table-hover table-bordered" style="font-size:12px;">
							<thead class="bg-light">
								<tr>
									<th>${__('Item')}</th>
									<th>${__('Group')}</th>
									<th class="text-right">${__('Qty Available')}</th>
									<th>${__('UOM')}</th>
								</tr>
							</thead>
							<tbody>
				`;
				
				r.message.forEach(row => {
					html += `
						<tr>
							<td><strong>${row.item_name}</strong><br><small class="text-muted">${row.item_code}</small></td>
							<td>${row.item_group}</td>
							<td class="text-right" style="font-weight:bold; color:var(--primary-color);">${row.actual_qty}</td>
							<td>${row.stock_uom}</td>
						</tr>
					`;
				});
				
				html += `
							</tbody>
						</table>
					</div>
					<div style="margin-top:15px; display:flex; gap:10px;">
						<button class="btn btn-xs btn-primary btn-stock-take">
							<i class="fa fa-check-square-o"></i> Start Stock Take
						</button>
						<button class="btn btn-xs btn-default btn-stock-entry">
							<i class="fa fa-plus"></i> New Stock Entry
						</button>
					</div>
				`;
				container.html(html);

				container.find('.btn-stock-take').on('click', () => {
					frappe.new_doc('Stock Reconciliation', {
						company: frm.doc.company,
						purpose: 'Stock Reconciliation'
					});
				});

				container.find('.btn-stock-entry').on('click', () => {
					frappe.new_doc('Stock Entry', {
						company: frm.doc.company,
						purpose: 'Material Receipt'
					});
				});

			} else {
				container.html(`
					<div class="alert alert-info" style="font-size:12px;">
						<i class="fa fa-info-circle"></i> ${__('No stock found in Veterinary Warehouse. Start by adding items via Stock Entry.')}
						<br><br>
						<button class="btn btn-xs btn-primary btn-stock-entry">
							<i class="fa fa-plus"></i> New Stock Entry
						</button>
					</div>
				`);
				container.find('.btn-stock-entry').on('click', () => {
					frappe.new_doc('Stock Entry', {
						purpose: 'Material Receipt'
					});
				});
			}
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

	// Add Serial Number column for traceability
	const display_columns = [{ label: '#', width: '40px' }, ...columns];

	const headers = display_columns.map(c => `<th style="white-space:nowrap;${c.width ? `width:${c.width};` : ''}">${c.label}</th>`).join('');
	const body = rows.map((row, index) => {
		const cells = display_columns.map((c, col_idx) => {
			if (col_idx === 0) return `<td>${index + 1}</td>`;

			let val = row[c.key] != null ? row[c.key] : '';
			
			// Strip HTML if it's a string (to handle Text Editor fields)
			if (typeof val === 'string' && val.includes('<')) {
				val = val.replace(/<[^>]*>?/gm, '');
			}

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