from django.views.generic import ListView

from photoblog.models import Entry

class EntryListView(ListView):
    model = Entry
    def get_queryset(self):
        return super(EntryListView, self).get_queryset()
