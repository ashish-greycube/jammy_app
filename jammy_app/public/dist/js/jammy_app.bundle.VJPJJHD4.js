(() => {
  // frappe-html:/home/ashish/v14-bench/apps/jammy_app/jammy_app/public/js/templates/head.html
  frappe.templates["head"] = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>{{ title }}</title>
    <link href="{{ base_url }}/assets/frappe/css/bootstrap.css" rel="stylesheet">
	<link type="text/css" rel="stylesheet"
        href="{{ base_url }}/assets/frappe/css/font-awesome.css">
	<style>
		{%= frappe.boot.print_css %}
	</style>
  </head>
  <body>
	  <div class="print-format-gutter">
		  <div id="header-html" class="visible-pdf">
		  	<div class="letter-head-header">
				<div class="row">
					<div class="col-xs-12">
						<img src= "/files/jammy_letter_head_logo.gif" style="width: 45%" >

					</div>
					
					<!-- <div class="col-xs-4">	
					</div>
					<div class="col-xs-4">
						style="width: 45%"
					</div>
					<div class="col-xs-4">
						<h3 class="text-right"><img src= "https://jammyinc.com/wp-content/themes/jammysite/images/img_01.png" width="100" height="100"></h3><br>

						<h3 class="text-right"><img src= "/files/jammy_logo.png"></h3><br>
					</div> -->
				</div>
			</div>
		  </div>
			<div id="footer-html" class="visible-pdf">
		  		<div class="letter-head-footer">
					<div class="row">
						<div class="col-xs-12">
								<b>JAMMY, INCORPORATED</b><br>
								PO Box 471697,Fort Worth, TX 76147 817.737.6566 / Fax 737.5960 / 800.537.3136/info@<b>jammyinc.com</b><br>
								
							
						</div>
					</div>
				</div>
		  	</div>
	   <div class="print-format">
       		{%= content %}
		</div>
  </body>
</html>
`;

  // frappe-html:/home/ashish/v14-bench/apps/jammy_app/jammy_app/public/js/templates/customer_statement.html
  frappe.templates["customer_statement"] = `{% $.each(data, function(i, record) { %}
{% if (i) { %}
{% count = 0 %}
<style type="text/css">table { page-break-inside:auto }</style>

<div class="">
	<div class="row">
		<div class="col-xs-6">
				<div>
					{%= filters.report_date %}<br><br>
				</div>
				<div>
					<p>
						<b>{{ i }} </b><br>
						{% if (data[i][0].address) { %}
						   {% if (data[i][0].address.address_line1) { %}
							   {{ data[i][0].address.address_line1 }}<br>
						   {% } %}
						    {% if (data[i][0].address.address_line2)  { %}
								{{ data[i][0].address.address_line2 }}<br>
						    {% } %}
		                    {% if (data[i][0].address.city) { %}
								{{ data[i][0].address.city }},
							{% } %}
							{% if (data[i][0].address.state) { %}
								{{ data[i][0].address.state }}&nbsp;
							{% } %}
							{% if (data[i][0].address.pincode) { %}
								{{ data[i][0].address.pincode }}
							{% } %}
							{% if (data[i][0].address.country !=  "United States") { %}
							<br>
								{{ data[i][0].address.country }}
							{% } %}
						{% } %}
					</p>
				</div>
		</div>
		<div class="col-xs-6" >
			<div class="">
				<p class="text-right" align="Center">
					{% count += 1 %}
					Page No {%= count %}
				</p>
			</div>
			<div class="" align="Right">
				<b>CUSTOMER STATEMENT</b>
			</div>
			<div class="" align="Right">
			</div>
		</div>
	</div>
	<br><br><br>
	<div class="">
		<table class="table">
			<thead>
				<tr>
					<th>Transaction Date</th>
					<th>Transaction No.</th>
					<th>Reference</th>
					<th>Voucher Type</th>
					<th>Due Date</th>
					<th style="text-align:right;">Amount(USD)</th>
				</tr>
			</thead>
			{% total_amount = 0.0; %}
			{% $.each(record, function(i, vouchers) { %}
				{% total_amount +=  flt(vouchers[__("outstanding")]) %}
				<tr>
					<td>{{ vouchers[__("posting_date")] }}</td>
					<td>{{ vouchers[__("voucher_no")] }}</td>
					<td>{{ vouchers[__("your_reference")] }}</td>
					<td>{{ vouchers[__("voucher_type")] }}</td>
					<td>{{ vouchers[__("due_date")] }}</td>
					<td style="text-align:right;">{{ vouchers[__("outstanding")] }}</td>
				</tr>
				{% if (i != 0 && i%15 ==0) { %}
					</table>
					</div>
					<div class="">
						<p style="page-break-after: always"> &nbsp;</p>
					</div>
					<div class="">
						<p class="text-right">
							{% count += 1 %}
							Page No {%= count %}
						</p>
					<table class="table">
						<thead>
							<tr>
								<th>Transaction Date</th>
								<th>Transaction No.</th>
								<th>Reference</th>
								<th>Voucher Type</th>
								<th>Due Date</th>
								<th style="text-align:right;">Amount(USD)</th>
							</tr>
						</thead>
				{% } %}
			{% }); %}
		</table>
	</div>
	<div class="">
		<div class="text-right">Total Balance: {%= format_currency(flt(total_amount)) %}</div>
	</div>
	<div class="">
		{%
			range_1 = 0.0;
			range_2 = 0.0;
			range_3 = 0.0;
			range_4 = 0.0;
			range_5 = 0.0;
		%}
		{% $.each(record, function(i,vouchers) { %}
			{% range_1 += flt(vouchers[__("range1")]) %}
			{% range_2 += flt(vouchers[__("range2")]) %}
			{% range_3 += flt(vouchers[__("range3")]) %}
			{% range_4 += flt(vouchers[__("range4")]) %}
			{% range_5 += flt(vouchers[__("range5")]) %}
		{% }); %}

		<table class="table table-borderless">
			<tr>
				<td style="text-align:center;">Total</td>
				<td style="text-align:center;">Current</td>
				<td style="text-align:center;">Past Due 1-{{ filters.range1 }}</td>
				<td style="text-align:center;">Past Due {%= filters.range1 + 1 %}-{{ filters.range2 }}</td>
				<td style="text-align:center;">Past Due {%= filters.range2 + 1 %}-{{ filters.range3 }}</td>
				<td style="text-align:center;">Past Due {%= filters.range3 + 1 %}-{{ filters.range4 }}</td>
				<td style="text-align:center;">Past Due {%= filters.range4 + 1 %}-above</td>
			</tr>
			<tr>
				<td style="text-align:center;">{%= format_currency(flt(total_amount)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(data[i][0].party_current_due_amount)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_1)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_2)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_3)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_4)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_5)) %}</td>

			</tr>
		</table>
	</div>
</div>
<div>.</div>
<div class="page-break"></div>
{% } %}
{% }); %}
`;

  // frappe-html:/home/ashish/v14-bench/apps/jammy_app/jammy_app/public/js/templates/customer_letter_print.html
  frappe.templates["customer_letter_print"] = `<html>
{% $.each(data, function(i, record) { %}

{% if (i) { %}
<div class="col-xs-12">
	<div class="row">
		<div class="col-xs-6">
				<div>
					{%= filters.report_date %}<br><br>
				</div>
				<div>
					<p>
						<b>{{ i }}</b> <br>
						{% if (data[i][0].address) { %}
						   {% if (data[i][0].address.address_line1) { %}
							   {{ data[i][0].address.address_line1 }}<br>
						   {% } %}
						    {% if (data[i][0].address.address_line2)  { %}
								{{ data[i][0].address.address_line2 }}<br>
						    {% } %}
		                    {% if (data[i][0].address.city) { %}
								{{ data[i][0].address.city }},
							{% } %}
							{% if (data[i][0].address.state) { %}
								{{ data[i][0].address.state }}&nbsp;
							{% } %}
							{% if (data[i][0].address.pincode) { %}
								{{ data[i][0].address.pincode }}
							{% } %}
							{% if (data[i][0].address.country != "United States") { %}
							<br>
								{{ data[i][0].address.country }}
							{% } %}
						{% } %}
					</p>
				</div>
		</div>
		<div class="col-xs-6" >

			<div class="" align="Right">
				<b>BALANCE NOTICE</b>
			</div>
			<div class="" align="Right">
			</div>
		</div>
	</div>

	<br><br><br>
	<div class="row">
		Dear {{i}},<br><br>
		{%
			range_1 = 0.0;
			range_2 = 0.0;
			range_3 = 0.0;
			range_4 = 0.0;
			range_5 = 0.0;
		%}
		{% total_pass_due = 0.0  %}
		{% total_amount = 0.0; %}
		{% $.each(record, function(i, vouchers) { %}
		    {% total_amount +=  flt(vouchers[__("outstanding")]) %}
		    {% range_1 += flt(vouchers[__("range1")]) %}
			{% range_2 += flt(vouchers[__("range2")]) %}
			{% range_3 += flt(vouchers[__("range3")]) %}
			{% range_4 += flt(vouchers[__("range4")]) %}
			{% range_5 += flt(vouchers[__("range5")]) %}
			{% payment_entry_date = vouchers[__("payment_entry_date")]  %}
		{% }); %}
		{% total_pass_due = range_1 + range_2 + range_3 + range_4 + range_5 %}


		<p align="justify" style="text-indent: 50px;">
			Our records indicate that your account is past due. We assume that this is an oversight on your part.
			The amount you have past due is {%= format_currency(flt(total_pass_due)) %} and your last payment was dated  {{ payment_entry_date }}.Please send
			payment as soon as possible to clear the past due balance.<br>
		</p>

	</div>
	<div class="row">
		<table class="table table-borderless">
			<thead>
				<td style="text-align:center;">Total</td>
				<td style="text-align:center;">Current</td>
				<td style="text-align:center;">Past Due 1-{{ filters.range1 }}</td>
				<td style="text-align:center;">Past Due {%= filters.range1 + 1 %}-{{ filters.range2 }}</td>
				<td style="text-align:center;">Past Due {%= filters.range2 + 1 %}-{{ filters.range3 }}</td>
				<td style="text-align:center;">Past Due {%= filters.range3 + 1 %}-{{ filters.range4 }}</td>
				<td style="text-align:center;">Past Due {%= filters.range4 + 1 %}-above</td>
			</thead>
			<tr>
				<td style="text-align:center;">{%= format_currency(flt(total_amount)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(data[i][0].party_current_due_amount)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_1)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_2)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_3)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_4)) %}</td>
				<td style="text-align:center;">{%= format_currency(flt(range_5)) %}</td>
			</tr>
		</table>
	</div>
	<div class="row">
		<p style="text-indent: 50px;">
			If you have any questions, please contact me at (800) 537-3136.<br>
			If you have mailed a payment in the last two weeks, please disregard this notice.
		</p>
	</div>
	<br><br>
	<div class="row">
	    Sincerely,
		<h3><b>Ana Espinosa</b></h3><br>
	</div>
	<div class="row">
	Ana Espinosa<br>
	Accounts Receivable<br>
	<b>JAMMY, INCORPORATED<br>
	(800) 537-3136</b>
	</div>
</div>
<div>.</div>
<div class="page-break"></div>
{% } %}
{% }); %}
</html>
`;

  // ../jammy_app/jammy_app/public/js/jammy_app.bundle.js
  console.log("ashish");
})();
//# sourceMappingURL=jammy_app.bundle.VJPJJHD4.js.map
