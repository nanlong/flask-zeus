from .base import BaseDetailView


class DetailView(BaseDetailView):

    def dispatch_request(self, **kwargs):
        stmt = self.get_query(**kwargs)
        item = stmt.first()
        context = self.get_context()
        context.update({
            'item': item
        })
        return self.render(**context)
