'''
Ver 1.0
- support to convert the xml results to txt and html results

Ver 1.1
- Add --deduplicate flag to remove duplicates messages in the result.
- Add --output-xlsx flag to support xlsx format results (openpyxl package is required)
- Add CERT/AUTOSAR columns in summary table of html and xlsx format results

Ver 1.2
- fix the bug that the message would be removed if the description is different but File/Line/Category are same
- Categorize the message into Misc if the message doesn't belong to any file.
- Merge the summary results for the same head file with different path expression in html and xlsx report.
For example, the following three expressions actually point to one head file 'diagnostics.h' but it will shown as 3 different files in summary report.
Now, this script supports to merge the messages of these 3 files into one in html and xlsx report.
xxx\includes\diagnostics.h
xxx\src/..\includes/diagnostics.h
xxx\src/..\includes\diagnostics.h

reference command
python generate-reports.py --input-xml xml_results.xml --input-xml-descriptions dump_messages_output.xml --output-text text_results.txt --output-html html_results.html --output-xlsx xlsx_results.xlsx --output-sarif sarif_results.sarif --deduplicate 1

SARIF export example:
pclp -os(xml_results.xml) env-xml.lnt -dump_messages(file=dump_messages_output.xml,format=xml) -oe(version.txt) -version \
    compiler.lnt project.lnt

python generate-reports.py --input-xml xml_results.xml --input-xml-descriptions dump_messages_output.xml --input-version-text version.txt --output-sarif sarif_results.sarif --deduplicate 1
'''



import sys
import xml.etree.ElementTree
import html
import argparse
import os
try:
    from openpyxl import Workbook
    from openpyxl.styles import colors, Font, Fill, NamedStyle
    from openpyxl.styles import PatternFill, Border, Side, Alignment
    from openpyxl.utils import get_column_letter
except ImportError as e:
    print ("openpyxl Package doesn't exist. Unable to generate spreadsheet result")
import json


summary_column_headers = ['File', 'Messages','Error','Warning','Info','Note','MISRA','CERT','AUTOSAR']
detailed_column_headers = ['File', 'Line', 'Category', '#', 'Description']

class Message:
    def __init__(self, file, line, category, number, text):
        self.file = file if file is not None else ''
        self.line = line
        self.category = category
        self.number = number
        self.text = text
        self.supplementals = []
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented
        return (self.file==other.file and self.line==other.line and self.category==other.category and self.number==other.number and self.text==other.text)

    def __hash__(self):
        return hash((self.file,self.line,self.category,self.number,self.text))

class FileSummary:
    def __init__(self, filename):
        self.msg_count = 0
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0
        self.note_count = 0
        self.supplemental_count = 0
        self.misra_count = 0
        self.cert_count = 0
        self.autosar_count = 0
        self.filename = filename

class MessageDescription:
    def __init__(self, number, category, text, commentary):
        self.number = number
        self.category = category
        self.text = text
        self.commentary = commentary
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented
        return (self.number==other.number and self.category==other.category and self.text == other.text and self.commentary==other.commentary)
    def __hash__(self):
        return hash((self.number, self.category, self.text, self.commentary))

def parse_msgs(filename,deduplicate):
    tree = xml.etree.ElementTree.parse(filename)
    root = tree.getroot()
    msgs = []
    duplicated_flag = 0
    last_primary_msg = None
    for child in root:
        msg = Message(
            child.find('file').text,
            child.find('line').text,
            child.find('type').text,
            child.find('code').text,
            child.find('desc').text
        )
        #coverts the file path to absolute path
        if msg.file !='' and msg.file != '<command line>':
            msg.file=os.path.abspath(msg.file)
        else:
            msg.file='Misc'
        if msg.category == "supplemental":
            last_primary_msg.supplementals.append(msg)
        else:
            last_primary_msg = msg
            msgs.append(msg)

    #remove the duplicated messages for the same line of the same file.
    if deduplicate:
        msgs_original=msgs
        msgs.reverse()
        msgs_new=list(set(msgs))
        msgs_new.sort(key = msgs_original.index)
    else:
        msgs_new=msgs

    return msgs_new

def parse_descriptions(filename):
    descriptions = []
    if filename:
        tree = xml.etree.ElementTree.parse(filename)
        root = tree.getroot()
        for child in root:
            descriptions.append(MessageDescription(
                child.get('id'),
                child.find('category').text,
                child.find('text').text,
                child.find('commentary').text))
    return descriptions

def parse_version(filename):
    with open(filename, "r") as file:
        text = file.read().strip()
        text = "".join(text.split()[:-1])  # Remove commit hash
        # Trim until first digit
        for i, c in enumerate(text):
            if c.isdigit():
                return text[i:]
    return ""

def summarize_files(msgs):
    file_summaries = dict()
    for msg in msgs:
        if msg.file not in file_summaries:
            file_summaries[msg.file] = FileSummary(msg.file)
        file_summary = file_summaries[msg.file]

        if msg.category == 'error':
            file_summary.error_count += 1
        elif msg.category == 'warning':
            file_summary.warning_count += 1
        elif msg.category == 'info':
            file_summary.info_count += 1
        elif msg.category == 'note':
            file_summary.note_count += 1
        elif msg.category == 'supplemental':
            file_summary.supplemental_count += 1

        if msg.category != 'supplemental':
            file_summary.msg_count += 1

        if 'MISRA' in msg.text:
            file_summary.misra_count += 1
        if 'CERT' in msg.text:
            file_summary.cert_count += 1
        if 'AUTOSAR' in msg.text:
            file_summary.autosar_count += 1
    return file_summaries

def build_html_table(column_headers, data_source, row_generator):
    out = ""
    out += "<table>"
    out += "<tr>"
    for header in column_headers:
        out += "<th scope=\"col\">"
        out += header
        out += "</th>"
    out += "</tr>"
    for item in data_source:
        out += "<tr>"
        row = row_generator(item)
        for data in row:
            out += "<td>"
            out += str(data)
            out += "</td>"
        out += "</tr>"
    out += "</table>"
    return out

def format_benign_zero(x):
    return str(x) if x != 0 else "<span class=\"zero\">" + str(x) + "</span>"

def emit_html(msgs):
    out = ""
    out += "<!DOCTYPE html><html>"
    out += "<head>"
    out += "<meta charset=\"utf-8\"><title>Report</title>"
    out += "<style>"
    out += "body { font-family: sans-serif; margin: 1em; }"
    out += "table { border-collapse: collapse; }"
    out += "td { padding: 0.25em; border: 1px solid #AAAAAA; }"
    out += "th { padding: 0.5em; }"
    out += ".filename { font-family: monospace; font-weight: bold; }"
    out += ".zero { color: #AAAAAA; }"
    out += "</style>"
    out += "</head>"
    out += "<body>"
    out += "<div>"
    out += "<h1>Report</h1>"
    out += "<h2>Summary</h2>"
    file_summaries = summarize_files(msgs)
    summary_total = FileSummary('Total')
    for file in file_summaries.values():
        summary_total.msg_count += file.msg_count
        summary_total.error_count += file.error_count
        summary_total.warning_count += file.warning_count
        summary_total.info_count += file.info_count
        summary_total.note_count += file.note_count
        summary_total.misra_count += file.misra_count
        summary_total.cert_count += file.cert_count
        summary_total.autosar_count += file.autosar_count
    file_summaries['Total'] = summary_total
    out += build_html_table(
        summary_column_headers,
        file_summaries.values(),
        lambda file: [
            ("<span class=\"filename\">" + html.escape(file.filename) + "</span>") if file.filename != 'Total' else file.filename,
            format_benign_zero(file.msg_count),
            format_benign_zero(file.error_count),
            format_benign_zero(file.warning_count),
            format_benign_zero(file.info_count),
            format_benign_zero(file.note_count),
            format_benign_zero(file.misra_count),
            format_benign_zero(file.cert_count),
            format_benign_zero(file.autosar_count)
        ]
    )
    out += "<br>"
    out += "<h2>Details</h2>"
    out += build_html_table(
        detailed_column_headers,
        msgs,
        lambda msg: [
            "<span class=\"filename\">" + html.escape(msg.file) + "</span>",
            msg.line,
            msg.category,
            msg.number,
            html.escape(msg.text)
        ]
    )
    out += "</div>"
    out += "</body>"
    out += "</html>\n"
    return out

def emit_text_msg(msg):
    out = ""
    if (msg.file and msg.file != "") or (msg.line and msg.line != '0'):
        out += msg.file + " " + str(msg.line) + " "
    out += msg.category + " " + str(msg.number) + ": "
    out += msg.text + "\n"
    for supplemental in msg.supplementals:
        out += emit_text_msg(supplemental)
    return out

def emit_text(msgs):
    out = ""
    for msg in msgs:
        out += emit_text_msg(msg)
    return out

def write_output(output, filename):
    with open(filename, 'w') as file:
        file.write(output)

def emit_xlsx_summary(msgs,worksheet):

    for first_row in worksheet.iter_rows(min_row=1, min_col=1, max_row=1, max_col=len(summary_column_headers)):
        for cell,header in zip(first_row,summary_column_headers):
            cell.value=header
    file_summaries = summarize_files(msgs)
    summary_total = FileSummary('Total')
    for file in file_summaries.values():
        summary_total.msg_count += file.msg_count
        summary_total.error_count += file.error_count
        summary_total.warning_count += file.warning_count
        summary_total.info_count += file.info_count
        summary_total.note_count += file.note_count
        summary_total.misra_count += file.misra_count
        summary_total.cert_count += file.cert_count
        summary_total.autosar_count += file.autosar_count
    file_summaries['Total'] = summary_total
    for cells,file in zip(worksheet.iter_rows(min_row=2, min_col=1, max_row=(len(file_summaries)+1), max_col=len(summary_column_headers)),file_summaries.values()):
        for cell,header in zip(cells,summary_column_headers):
            if header == "File":
                cell.value=file.filename
            elif header =="Messages":
                cell.value=file.msg_count
            elif header =="Error":
                cell.value=file.error_count
            elif header =="Warning":
                cell.value=file.warning_count
            elif header =="Info":
                cell.value=file.info_count
            elif header =="Note":
                cell.value=file.note_count
            elif header =="MISRA":
                cell.value=file.misra_count
            elif header =="CERT":
                cell.value=file.cert_count
            elif "AUTOSAR":
                cell.value=file.autosar_count

    for cells in worksheet.iter_rows():
        for cell in cells:
            cell.alignment = Alignment(horizontal='left',vertical='center',wrapText=True)
            cell.font = Font(name='Calibri', color='000000', size=14, b=True,bold=0)

    for column_cells in worksheet.columns:
        new_column_length = max(len(str(cell.value)) for cell in column_cells)
        new_column_letter = (get_column_letter(column_cells[0].column))
        if new_column_length > 0:
            worksheet.column_dimensions[new_column_letter].width = 11.5

    worksheet.column_dimensions['A'].width = 50


def emit_xlsx_detailed(msgs,worksheet):
    for first_row in worksheet.iter_rows(min_row=1, min_col=1, max_row=1, max_col=len(detailed_column_headers)):
        for cell,header in zip(first_row,detailed_column_headers):
            cell.value=header
    for cells,msg in zip(worksheet.iter_rows(min_row=2, min_col=1, max_row=(len(msgs)+1), max_col=len(detailed_column_headers)),msgs):
        for cell,header in zip(cells,detailed_column_headers):
            if header == "File":
                cell.value=msg.file
            elif header =="Line":
                cell.value=msg.line
            elif header =="Category":
                cell.value=msg.category
            elif header =="#":
                cell.value=msg.number
            elif header =="Description":
                cell.value=msg.text

    for cells in worksheet.iter_rows():
        for cell in cells:
            cell.alignment = Alignment(horizontal='left',vertical='center',wrapText=True)
            cell.font = Font(name='Calibri', color='000000', size=12, b=True,bold=0)

    worksheet.column_dimensions['A'].width = 40
    worksheet.column_dimensions['B'].width = 10
    worksheet.column_dimensions['C'].width = 10
    worksheet.column_dimensions['D'].width = 10
    worksheet.column_dimensions['E'].width = 120

def emit_xlsx(msgs,filename):
    wb = Workbook()
    ws = wb.active
    ws.title="Summary"
    emit_xlsx_summary(msgs,ws)
    ws=wb.create_sheet("Detailed")
    emit_xlsx_detailed(msgs,ws)
    try:
        wb.save(filename)
    except Exception as e:
        print ("Warning: " + filename + " is open. Please close the spreadsheet and run the script again.")

def emit_sarif(msgs, descriptions, filename, version):
    report = {
        "$schema": "https://docs.oasis-open.org/sarif/sarif/v2.1.0/cos02/schemas/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "PC-lint Plus",
                    "version": version,
                    "informationUri": "https://pclintplus.com",
                    "rules": []
                }
            },
            "artifacts": [],
            "results": []
        }]
    }

    # Rules
    rule_id_set = { msg.number for msg in msgs }
    # Filter out descriptions that messages were not emitted for
    filtered_descriptions = [ desc for desc in descriptions if desc.number in rule_id_set ]
    for desc in filtered_descriptions:
        report["runs"][0]["tool"]["driver"]["rules"].append({
            "id": "PCLP" + desc.number,
            "name": desc.text,
            "shortDescription": { "text": desc.commentary }
        })

    # Artifacts
    files = { msg.file for msg in msgs }
    for msg in msgs:
        files.update({ supp.file for supp in msg.supplementals })
    for file in files:
        report["runs"][0]["artifacts"].append({ "location": { "uri": "file:///" + file.replace("\\", "/").lstrip("/") } })
    name_to_index = { file: i for i, file in enumerate(files) }

    # Results
    for msg in msgs:
        if msg.category == 'info':
            msg.category = 'note'
        result = {
            "ruleId": "PCLP" + msg.number,
            "level": msg.category,
            "message": { "text": msg.text },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": { "index": name_to_index[msg.file] },
                    "region": { "startLine": max(int(msg.line), 1) }
                }
            }],
            "relatedLocations": []
        }
        # Add supplementals as related locations
        for i, supp in enumerate(msg.supplementals, start=0):
            result["relatedLocations"].append({
                "id": i,
                "message": { "text": supp.text },
                "physicalLocation": {
                    "artifactLocation": { "index": name_to_index[supp.file] },
                    "region": { "startLine": max(int(supp.line), 1) }
                }
            })
        report["runs"][0]["results"].append(result)

    with open(filename, 'w') as file:
        json.dump(report, file, indent=2)

def main():

    parser = argparse.ArgumentParser(description='Generate HTML or text output from PC-lint Plus XML reports')
    parser.add_argument('--input-xml', action='store', help='XML input filename', required=True)
    parser.add_argument('--input-xml-descriptions', action='store', help='XML input filename', required=False)
    parser.add_argument('--input-version-text', action='store', help='Version text input filename', required=False)
    parser.add_argument('--output-text', action='store', help='Text output filename', required=False)
    parser.add_argument('--output-html', action='store', help='HTML output filename', required=False)
    parser.add_argument('--output-xlsx', action='store', help='Spreadssheet output filename', required=False)
    parser.add_argument('--output-sarif', action='store', help='SARIF output filename', required=False)
    parser.add_argument('--deduplicate', action='store', default=0, type=int,help='Remove the duplicated messages. 1==ON and 0==OFF', required=False)
    args = parser.parse_args()

    if not (args.output_text or args.output_html or args.output_xlsx or args.output_sarif):
        parser.error("no output destination specified")

    msgs = parse_msgs(args.input_xml,args.deduplicate)
    msgs.sort(key=lambda msg: (msg.file == "", msg.file, int(msg.line) if msg.line != "" else 0))
    descriptions = parse_descriptions(args.input_xml_descriptions)
    version = parse_version(args.input_version_text)

    if args.output_text:
        write_output(emit_text(msgs), args.output_text)
    if args.output_html:
        write_output(emit_html(msgs), args.output_html)
    if args.output_xlsx:
        emit_xlsx(msgs,args.output_xlsx)
    if args.output_sarif:
        emit_sarif(msgs, descriptions, args.output_sarif, version)


if __name__ == "__main__":
    main()
