from django import forms

class QuillAdminWidget(forms.Textarea):
    """
    Rich Text WYSIWYG Editor widget powered by Quill.js with local offline assets,
    Word-like formatting toolbar, text highlights, and travel emoji palette.
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'quill-wysiwyg-editor',
            'rows': 8,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        css = {
            'all': (
                'vendor/quill/quill.snow.css',
                'admin/css/quill_admin.css',
            )
        }
        js = (
            'vendor/quill/quill.min.js',
            'admin/js/quill_admin.js',
        )
