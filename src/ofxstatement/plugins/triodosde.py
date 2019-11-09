import csv

from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import Statement, StatementLine, BankAccount, recalculate_balance
from pdb import set_trace as bp


class TriodosDePlugin(Plugin):
    """German Triodos plugin for ofxstatement
    """

    def get_parser(self, filename):
        f = open(filename, 'r', encoding=self.settings.get("charset", "ISO-8859-1"))
        parser = TriodosDeParser(f)
        return parser


class TriodosDeParser(CsvStatementParser):
    date_format = "%d.%m.%Y"
    mappings = {
        'date': 0,
        'payee': 3,
        'memo': 8,
        'amount': 11
    }

    def __init__(self, filename):
        self.statement = Statement('TRIODEF1', None,'EUR')
        self.fin = filename
        self.statement.currency = 'EUR'

    def parse(self):
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        stmt = super(TriodosDeParser, self).parse()
        recalculate_balance(stmt)
        return stmt

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        return csv.reader(self.fin, delimiter=';')

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """
        stmtline = super(TriodosDeParser, self).parse_record(line)
        """ As the amount is always positive, we negate it,
        if the amount is debit (= S[oll])
        """
        if line[12] == "S":
            stmtline.amount = -stmtline.amount
        return stmtline

    def parse_float(self, value):
        """Return a float from a string with ',' as decimal mark.
         ex. 1.234,56 -> 1234.56
        """
        return float(value.replace('.','').replace(',', '.'))
