import pdfkit
# import MySQLdb
import os
from jammy_app.jammy_app.report.customer_statement.customer_statement import *

def convert_pdf(customer_statement_file,customer_letter_file):
	try:
		site_path = os.getcwd()
		current_site = open("currentsite.txt","r")
		sitename = current_site.read()
		path =  site_path+"/"+sitename
		pdf_file= path+'/public/files/'+str(customer_statement_file).replace('.html', '.pdf')
		pdfkit.from_file(path+'/public/files/'+str(customer_statement_file), pdf_file)
		pdf_file= path+'/public/files/'+str(customer_letter_file).replace('.html', '.pdf')
		pdfkit.from_file(path+'/public/files/'+str(customer_letter_file), pdf_file)

	except Exception as e:
		raise e
