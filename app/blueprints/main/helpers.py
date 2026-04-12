import csv
import io
from flask import send_file

def generate_csv_template(columns):
    """Generuje obiekt BytesIO zawierający plik CSV z nagłówkami."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    
    # Przekonwertuj na BytesIO dla Flask send_file
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    return mem
