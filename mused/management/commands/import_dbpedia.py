import bonobo
from bonobo.ext.django import ETLCommand


class Command(ETLCommand):
    def extract(self):
        yield 'a'
        yield 'b'
        yield 'c'

    def transform(self, s):
        yield s.upper()

    def load(self, s):
        self.stdout.write(s)

    def get_graph(self, *args, **options):
        return bonobo.Graph(
            self.extract,
            self.transform,
            self.load,
        )
